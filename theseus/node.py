from collections import Counter
import matplotlib.pyplot as plt

class Node:
    def __init__(self, documents=[], name='anon'):
        """documents is a file with one doc per line"""
        self.counter = Counter()
        self.load(documents)
        self.documents = documents
        self.profile = []
        self.name = name
        self.cutoff = 100
        self.depth = 100

    def load(self, documents):
        assert documents, "missing list of documents, text single doc per line"
        assert (isinstance(documents, list) and isinstance(documents[0], list))
        for document in documents:
            self.counter += Counter(document)
        return self

    def get_frequencies(self, limit=10):
        total = sum(self.counter.values())
        return {key: float(val) / total for key, val in self.counter.most_common(limit)}

    def num_keys(self):
        return len(self.counter.keys())

    def keys_sorted_by_frequency(self, cutoff=100):
        return [key for key, _ in self.counter.most_common()][:cutoff]

    def create_profile(self, node_y, ratio=0.5):
        x, y, keys = self.create_xy_table(node_y, cutoff=100, ratio=ratio)
        self.profile = [row[0] for row in zip(keys, zip(x, y))]
        return self.profile

    def create_xy_table(self, node2, cutoff=100, ratio=20.0):
        keys1 = self.keys_sorted_by_frequency(cutoff=cutoff)
        keys2 = node2.keys_sorted_by_frequency(cutoff=cutoff)

        freq1 = self.get_frequencies(limit=cutoff)
        freq2 = node2.get_frequencies(limit=cutoff)
        x, y = [], []
        reversed(keys2)
        final_keys = []
        for key in keys1:
            f1, f2 = freq1.get(key, 0), freq2.get(key, 0)
            if f1 != 0 and f2/(f1 + 0.001) < ratio:
                x.append(f1)
                y.append(f2)
                final_keys.append(key)
        return x, y, final_keys

    def visualize(self, background, num_labeled=10, magnification=1.0, viz=True, cutoff=100):
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
        area = self.profile[:self.depth]
        hits = len(set(inputs) & set(area))
        return hits >= self.cutoff

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
