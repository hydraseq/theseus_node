from collections import Counter

class Node():
    def __init__(self, documents=[]):
        self.counter = Counter()
        if documents:
            self.load(documents)

    def load(self, documents):
        assert isinstance(documents, list)
        assert isinstance(documents[0], list)

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

def create_xy_table(node1, node2, cutoff1=100, cutoff2=100, ratio=20.0):
    assert node2.num_keys() >= node1.num_keys()
    keys1 = node1.keys_sorted_by_frequency()
    keys2 = node2.keys_sorted_by_frequency()

    freq1 = node1.get_frequencies(limit=cutoff1)
    freq2 = node2.get_frequencies(limit=cutoff2)

    x, y = [], []
    reversed(keys2)
    #keys1.extend(keys2)
    final_keys = []
    for key in keys1:
        f1, f2 = freq1.get(key, 0), freq2.get(key, 0)
        if f1 != 0 and f2/(f1 + 0.001) < ratio:
            x.append(f1)
            y.append(f2)
            final_keys.append(key)

    return x, y, final_keys

####################################################################################
#  Visualization.  Might want to move this to own file with helpers
####################################################################################
import matplotlib.pyplot as plt
def visualize(node, background, num_labeled=10, axis_lims=(0.0, 1.0), magnification=1):
    lst_x, lst_y, keys = create_xy_table(node, background)
    lst_x = [x * magnification for x in lst_x]
    lst_y = [y * magnification for y in lst_y]
    fig, ax = plt.subplots()
    low, high = axis_lims
    ax.set_xlim(low, high)
    ax.set_ylim(low, high)
    ax.set_aspect('equal')
    ax.scatter(lst_x, lst_y)

    for i, txt in enumerate(keys):
        if i > num_labeled: txt = ''
        ax.annotate(txt, (lst_x[i],lst_y[i]))

    plt.show()