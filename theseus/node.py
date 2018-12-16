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
        return {key:float(val)/total for key, val in self.counter.most_common(limit)}
    def num_keys(self):
        return len(self.counter.keys())
    def keys_sorted_by_frequency(self):
        return [key for key, _ in self.counter.most_common()]

def create_xy_table(node1, node2):
    assert node2.num_keys() >= node1.num_keys()
    sorted_keys = node2.keys_sorted_by_frequency()
    freq1 = node1.get_frequencies(100)
    freq2 = node2.get_frequencies(100)

    x, y = [], []
    for key in sorted_keys:
        x.append(freq1.get(key, 0))
        y.append(freq2.get(key, 0))

    return x, y, sorted_keys