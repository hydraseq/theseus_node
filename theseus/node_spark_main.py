#get word list (train)
pathIn = '/home/ec2-user/projects/closure/data/bucket_5/2019-07-23-01/train/'
uniquify = True
segment = 'restaurant'
word = WordFrequncySpark(pathIn, uniquify, segment)

data = word.load_file()
data = word.clean_file(data)
word_ratio_df = word.compute_word_ratio(data)
word_context_df = word.grab_word_content_driver(word_ratio_df, data)


#flag biz using word list (predict)
pathIn = '/home/ec2-user/projects/closure/data/bucket_5/2019-07-23-01/test/'
uniquify = True
segment = 'restaurant'
word = WordFrequncySpark(pathIn, uniquify, segment)
word_df = pd.read_csv('/home/ec2-user/projects/index/analytics/review_word_count_analysis/health_safety_flag_words.csv')
word_list = word_df.word.to_list()

data_pred = word.load_file()
data_pred = word.clean_file(data_pred)
data_agg, flag_word_count_agg = word.flag_word_in_doc(data_pred, word_list)

