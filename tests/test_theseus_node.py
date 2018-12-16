import sys
import os
test_path = os.path.dirname(__file__)
sys.path.append("/Users/niarfe/tmprepos/theseus_node/")
import theseus
import data


def test_theseus_node_smoke():
    thn = theseus.Node(data.documents)
    assert thn.counter.most_common(2) == [('Python', 4), ('R', 4)]

def test_get_frequency():
    thn = theseus.Node(data.documents)
    assert thn.get_frequencies(2) == {'Python': 0.05970149253731343, 'R': 0.05970149253731343}

def test_compare_doc_to_background():
    background = theseus.Node(data.documents)
    first = theseus.Node(data.documents[:1])

    assert first.get_frequencies(2) == {'Big Data': 0.14285714285714285, 'Hadoop': 0.14285714285714285}

def test_assert_xy_table():
    background = theseus.Node(data.documents)
    first = theseus.Node(data.documents[:1])

    x, y, keys = theseus.node.create_xy_table(first, background)
    lenkeys = len(keys)
    assert len(x) == lenkeys
    assert len(y) == lenkeys
    assert sorted(keys[:5]) == sorted(['Big Data', 'HBase', 'Java', 'Python', 'R'])
    assert x[:3] == [0, 0, 0.14285714285714285]
    assert y[:3] == [0.05970149253731343, 0.05970149253731343, 0.04477611940298507]
