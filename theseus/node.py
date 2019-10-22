from collections import Counter
import matplotlib.pyplot as plt
import re

def default_tokenizer(txt):
    txt = re.sub(r'[^\w]', ' ', txt)
    return txt.lower().split()

class Node:
    """Encapsulates a counter object to track count, and calculate frequency of words in a set of docs"""
    def __init__(self, documents=[[]], name='anon'):
        """
        Args:
            documents, list<list<str>> list of list, where eas sublist is a document
        """
        self.counter = Counter()
        self.load(documents)
        self.profile = []
        self.name = name
        self.cutoff = 100
        self.depth = 100

    def load(self, documents, uniquify=False):
        """Load a list of list of words, already processed, directly"""
        assert documents,                      "missing list of documents, text single doc per line"
        assert isinstance(documents,    list), "documents must be list"
        assert isinstance(documents[0], list), "each document is also a list"
        #--------------------------------------------------------------------------------------------

        def _get_new_counts(document):
            return Counter(document) if not uniquify else Counter(list(set(document)))

        for idx, document in enumerate(documents):
            new_counter = _get_new_counts(document)
            self.counter.update(new_counter)
            if idx % 1000 == 0:
                print("load: {}\r".format(idx), end='')
        return self

    def load_file(self, fpath, tokenizer=None, uniquify=False):
        """Load a flat file, with one document per line, no header, no csv"""
        assert isinstance(fpath, str), "fpath must be type str not {}".format(type(fpath))
        tokenizer = default_tokenizer if tokenizer == None else tokenizer
        #----------------------------------------------------------------------------------

        with open(fpath, 'r') as source:
            for idx, line in enumerate(source):
                words = list(set(tokenizer(line))) if uniquify else tokenizer(line)
                self.counter.update(words)
                d = {k:v for k, v in self.counter.most_common(200)}
                self.counter = Counter(d)
                if idx % 1000 == 0:
                    print(" '{}\r".format(idx), end="")
        return self

    def trim_counter(self, depth):
        """Trim the counter member variable to only the top most common as per depth given"""
        assert isinstance(depth, int), "Depth must be an integer"
        #-------------------------------------------------------

        d = { k:v for k, v in self.counter.most_common(depth) }
        self.counter = Counter(d)
        return self


    def merge(self, node, depth=200):
        """Merte the counds in this node with the given node"""
        assert isinstance(node, Node), "Merge node must be type Node"
        #------------------------------------------------------------

        self.counter.update(node.counter)
        self.trim_counter(depth)
        return self

    def get_frequencies(self, limit=10):
        """Get the hightest frequency words"""
        total = sum(self.counter.values())
        return {key: float(val) / total for key, val in self.counter.most_common(limit)}

    def num_keys(self):
        """How many words are there"""
        return len(self.counter.keys())

    def keys_sorted_by_frequency(self, cutoff=100):
        """return the highest rated frequency words"""
        return [key for key, _ in self.counter.most_common()][:cutoff]

    def create_profile(self, node_y, cutoff=100, ratio=0.5):
        """Build the profile for this node against another.
        This node is along the x axis, while the other will be the y axis.
        The ratio is used to determine the cutoff of words.
        Return a list of top 100 highest to lowet rated words and their freqeuncies for x,y
        """
        _, _, self.profile = self.create_xy_table(node_y, cutoff=100, ratio=ratio)
        return self.profile

    def create_xy_table(self, node2, cutoff=100, ratio=20.0):
        """This creates the raw comparison between two nodes.
        Creates a 'table' consisting of three columns.
        x-frequency
        y-frequency
        word
        Returns three lists for each of them in descending order
        """
        keys1 = self.keys_sorted_by_frequency(cutoff=cutoff)
        freq1 = self.get_frequencies(limit=cutoff)
        freq2 = node2.get_frequencies(limit=cutoff)

        x, y, final_keys = [], [], []
        for key in keys1:
            f1, f2 = freq1.get(key, 0), freq2.get(key, 0)
            if f1 != 0 and f2/(f1 + 0.001) < ratio:
                x.append(f1)
                y.append(f2)
                final_keys.append(key)
        return x, y, final_keys

    def show_top(self, node2, cutoff=20, ratio=0.5):
        x, y, keys = self.create_xy_table(node2, ratio=ratio)
        
        with open(self.name+'.csv', 'w') as target:
            for x,y,word in zip(x,y,keys):
                target.write("{},{},{}\n".format(str(x),str(y),word))
                print("%.4f" % x,"%.4f" % y,word)
                cutoff -= 1
                if cutoff <= 0:
                    break

    def visualize(self, background, num_labeled=10, magnification=1.0, viz=True, cutoff=100):
        """create a scatter plot of this node against the background node
        If viz=False, a jpg is saved to disk instead.
        """
        
        assert magnification >= 1.0
        lst_x, lst_y, keys = self.create_xy_table(background, cutoff=cutoff)
        fig, ax = plt.subplots()
        low, high = 0.0, round(float(1)/magnification, 1)
        ax.set_xlim(low, high)
        ax.set_ylim(low, high)
        ax.set_aspect('equal')
        ax.scatter(lst_x, lst_y)

        for idx, key in enumerate(keys):
            if idx > num_labeled: txt = ''
            ax.annotate(key, (lst_x[idx],lst_y[idx]))

        if viz:
            plt.show()
        else:
            name = self.name if self.name else 'anon'
            plt.savefig(name)

    def predict(self, inputs):
        """If intersect between self.profile and inputs is >= self.profile[:self.depth], return True"""
        assert isinstance(inputs, list), "inputs must be a list of words"
        assert self.profile, "predict: self.profile must be calculated before we can predict"
        #-------------------------------------------------------------------------------

        area = self.profile[:self.depth]
        hits = len(set(inputs) & set(area))
        return hits >= self.cutoff

    def serialize(self):
        with open(self.name+'.py', 'w') as target:
            target.write(str(dict(self.counter)))

    def deserialize(self, fpath):
        str_dict =  open(fpath, 'r').read()
        self.counter = Counter(eval(str_dict))


    def __repr__(self):
        return "<"+self.name+" profile-len: "+str(len(self.profile))+">"


from collections import defaultdict
import csv
class Theseus:
    def __init__(self, table_csv=None, headers=True, target_col=-1, amorphous=False):
        """Generate nodes and implement helper functions to classify based on Theseus Nodes
            table_csv: path to a file containing data in csv format
            headers:   bool, use table headers as features in combination with values
            target_col: int, which column has the target values
            amorphous: bool, if True, assume each vertical is a feature, otherwise it's a word soup
        """
        self.target_col = target_col
        features = defaultdict(list)

        with open(table_csv, 'r') as fhandle:
            source = csv.DictReader(fhandle) if headers else fhandle
            for line in source:
                features[line[target_col]].append([str(key)+'-'+str(value) for key, value in line.items() if key != target_col])

        self.nodes = {name: Node(documents=documents, name=name) for name, documents in features.items()}
        docs = []
        [docs.extend(node.documents) for _, node in self.nodes.items()]
        self.nodes['background'] = Node(documents=docs, name="background")

    def build_up_nodes(self, ratio=0.2):
        for _, node in self.nodes.items():
            docs = []
            [docs.extend(n.documents) for k, n in self.nodes.items() if n != node.name]
            node.create_profile(Node(documents=docs), ratio=ratio)
        for key, node in self.nodes.items():
            print(key, node.profile)
        return self

    def viz_all(self):
        # TODO: can include the label as key to id the graphs
        for key, node in self.nodes.items():
            if key == 'background':
                continue
            node.visualize(self.nodes['background'], cutoff=100, magnification=10)

    def classify(self, s, cutoff=2):
        labels = []
        for _key, _node in self.nodes.items():
            if _key == 'background':
                continue
            _node.cutoff = cutoff
            if _node.predict(s):
                labels.append(_key)
        return labels

    def __repr__(self):
        return "<#nodes: "+str(len(self.nodes))+" nodes: "+str(self.nodes)+">"
