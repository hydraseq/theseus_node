import re
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import pyspark.sql.types as tps
import pyspark.sql.functions as fn

from lib.utility.decorators import typed_udf
from lib.utility.text.clean import text_clean
from lib.extract.naics2segment import naics2segment

spark = SparkSession \
    .builder \
    .master("local[*]") \
    .appName("CLOSURE Classifier") \
    .config('spark.cores.max', '7') \
    .config("spark.driver.cores", '1') \
    .config("spark.driver.memory", '6g') \
    .config('spark.executor.cores', '7') \
    .config("spark.executor.memory", '8g') \
    .config("spark.memory.fraction", '0.8') \
    .getOrCreate()

class WordFrequncySpark:
    def __init__(self, pathIn, uniquify=True, segment='restaurant', biz_min_review_count = 3):
        self.pathIn = pathIn
        self.uniquify = uniquify
        self.segment = segment
        self.biz_min_review_count = biz_min_review_count
        self.clean_string_dict = {'lower_case': True, 'remove_number': True, 'remove_punctuation': True, 'stem': True,
                  'remove_stop_words': True, 'remove_whitespace': True, 'remove_all_whitespace': False}
        self.top_word_count = 20
        self.word_context_len = 2


    def load_file(self):
        print('=== reading in data {}'.format(self.pathIn))
        data = spark.read.json('{}part*.json*'.format(self.pathIn))

        return data


    def clean_file(self, data):
        print('=== getting business name and segments')
        data = data.withColumn("name", fn.col("business").getField("name"))
        data = data.withColumn('segments', naics2segment(data.business.naics))

        print('=== getting is_closed')
        data = data.withColumn("is_closed", fn.col("business").getField("is_closed"))

        print('=== getting index scores')
        data = data.withColumn('customer_review', fn.col('carpe_indexes').getField('customer_review').getField('score'))

        print('=== getting review content, stars')
        data = data.withColumn("content", fn.explode_outer(fn.col("reviews")))
        data = data.withColumn("text_raw", fn.col("content").getField("content"))
        data = data.withColumn("stars", fn.col("content").getField("stars"))

        print('=== cleaning data')
        data = data.select(['id','name','text_raw','stars',"segments", "is_closed","customer_review"])
        data = data.where(fn.col('segments') == self.segment)
        data = data.where(fn.col('text_raw').isNull() == False)
        data = data.where(fn.col('stars').isNull() == False)
        data = data.dropDuplicates()
        data = data.withColumn('text', text_clean(fn.col('text_raw'),self.clean_string_dict,stopwords='default'))

        print('=== convert text to a list')
        if self.uniquify:
            data = data.withColumn('text_list', fn.array_distinct(fn.split('text', ' ')))
        else:
            data = data.withColumn('text_list', fn.split('text', ' '))

        return data


    def count_all_words_for_entire_col(self, data, text_col): 
        data_rdd = data.select([text_col]).rdd
        data_word_count = data_rdd.flatMap(lambda xs: [x[0] for x in xs]) \
                                .map(lambda x: (x, 1))\
                                .reduceByKey(lambda x, y: x + y)\
                                .sortBy(lambda x: x[1], ascending=False).collect()

        return data_word_count


    def compute_word_ratio(self, data):
        data_star1 = data.where(fn.col('stars') == 1)

        print('=== counting words for all data and 1-star data')
        data_word_count_list       = self.count_all_words_for_entire_col(data, 'text_list')
        data_word_count_star1_list = self.count_all_words_for_entire_col(data_star1, 'text_list')
        data_word_count_df       = pd.DataFrame(data=data_word_count_list, columns=['word','all_count'])
        data_word_count_star1_df = pd.DataFrame(data=data_word_count_star1_list, columns=['word','star1_count'])

        print('=== calculating words ratio for all data and 1-star data')
        if self.uniquify:
            data_count       = data.count()
            data_star1_count = data_star1.count()
        else:
            data_count       = data_word_count_df.all_count.sum()
            data_star1_count = data_star1_count.star1_count.sum()
        data_word_count_df['all_word_ratio']         = data_word_count_df.all_count.apply(lambda v: v/data_count)
        data_word_count_star1_df['star1_word_ratio'] = data_word_count_star1_df.star1_count.apply(lambda v: v/data_star1_count)

        print('=== merging 1-star data to all data')
        data_word_count_compare = data_word_count_star1_df.merge(data_word_count_df, on ='word', how = 'right')
        
        print('=== calculating word frequncy in 1-star data / word frequncy in all data')
        data_word_count_compare['star1_to_all_ratio'] = data_word_count_compare.star1_word_ratio / data_word_count_compare.all_word_ratio
        data_word_count_compare.sort_values(by='star1_to_all_ratio', ascending=False, inplace=True)

        return data_word_count_compare


    def grab_word_content_driver(self, data_word_count_compare, data):
        @typed_udf(tps.ArrayType(tps.StringType()))
        def grab_word_content(text_list, word, word_context_len):
            try:
                word_index = text_list.index(word)
                text_list_len = len(text_list)
                index_st = max(0,(word_index - word_context_len))
                index_ed = min(text_list_len, (word_index + word_context_len)) + 1
                word_context_list = text_list[index_st : index_ed]
            except:
                word_context_list = ['cannot find word']

            return word_context_list

        print('=== creating text list without dropping the duplicates')
        data = data.withColumn('text_list_raw', fn.split('text', ' '))

        top_word_list = data_word_count_compare.word[:self.top_word_count].tolist()
        top_word_context_count_df = pd.DataFrame()
        for word in top_word_list:
            print(word)
            word_col = '{}_word_context'.format(word)
            
            print('=== grabbing {} word context'.format(word))    
            data = data.withColumn(word_col, grab_word_content(fn.col('text_list_raw'), fn.lit(word), fn.lit(self.word_context_len)))
            data_w_word = data.where(fn.array_contains(word_col,'cannot find word')==False)

            print('=== counting word context')
            data_context_count_list = self.count_all_words_for_entire_col(data_w_word, word_col)
            data_context_count_df = pd.DataFrame(data=data_context_count_list, columns=['word_in_context','count'])
            
            print('=== removing word {} from word context list'.format(word))
            data_context_count_df = data_context_count_df[data_context_count_df.word_in_context != word]

            print('=== appending data_context_count_list to top_word_context_count_list')
            data_context_count_df['word'] = word
            top_word_context_count_df = top_word_context_count_df.append(data_context_count_df)

        top_word_context_count_df = top_word_context_count_df[['word','word_in_context','count']]
        
        return top_word_context_count_df


    def flag_word_in_doc(self, data, word_list):
        @typed_udf(tps.IntegerType())
        def find_given_words_for_single_row_set(sentence, word_list_str):
            word_list = word_list_str.split(',')
            if len(set(word_list) & set(sentence)) == 0:
                return 0
            else:
                return 1

        @typed_udf(tps.StringType())
        def find_given_words_for_single_row_set_return_flag_word(sentence, word_list_str):
            word_list = word_list_str.split(',')
            flag_word_list = list(set(word_list) & set(sentence))
            if len(flag_word_list) == 0:
                return 'None'
            else:
                return ','.join(flag_word_list)


        @typed_udf(tps.IntegerType())
        def find_given_words_for_single_row_loop(sentence, word_list_str):
            word_list = word_list_str.split(',')
            match_word = 0
            for word in word_list:
                if word in sentence:
                    match_word = 1
                    break
            return match_word


        print('=== counting word count for 1-star and 2-setar reviews given word list')
        word_list_str = ','.join(word_list)
        data = data.withColumn('flag_word', fn.when(fn.col('stars')>2, 0).\
                                        otherwise(find_given_words_for_single_row_set(fn.col('text_list'), fn.lit(word_list_str))))

        print('=== aggregating flag_word to biz level')
        data_agg = data.groupBy(['id','name', 'segments', 'is_closed','customer_review'])\
                       .agg(fn.sum('flag_word').alias('flag_word_sum'), \
                            fn.count('stars').alias('total_review_count'), \
                            fn.count(fn.when(fn.col("stars") < 3, True)).alias('star_1_2_count'))

        print('=== removing biz has less than {} reviews'.format(biz_min_review_count))
        data_agg = data_agg.where(fn.col('total_review_count') >= self.biz_min_review_count)

        print('=== calculating flag_word_ratio for each biz')
        data_agg = data_agg.withColumn('flag_word_ratio', fn.col('flag_word_sum') / fn.col('total_review_count'))
        data_agg = data_agg.orderBy('flag_word_ratio', ascending=False)

        print('=== count biz flag word count')
        flag_word_count_agg = data_agg.groupBy('flag_word_sum').count().orderBy('flag_word_sum', ascending=True)


        return data_agg, flag_word_count_agg
