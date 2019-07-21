import theseus as th
import sys

_ratio = float(sys.argv[1])

n_casko = th.Node()
n_casko.load_file('tests/data/poe/poe_cask_of_amontillado.txt')
print(len(n_casko.documents))

n_raven = th.Node()
n_raven.load_file('tests/data/poe/poe_raven.txt')
print(len(n_raven.documents))


n_backg = th.Node()
n_backg.load_file('tests/data/poe/poe_cask_of_amontillado.txt')
n_backg.load_file('tests/data/poe/poe_raven.txt')

print(n_raven, n_casko, n_backg)
print(len(n_raven.documents), len(n_casko.documents), len(n_backg.documents))

#n_casko.visualize(n_backg, magnification=500)
x, y, keys = n_casko.create_xy_table(n_backg, ratio=_ratio)

cutoff = 20
for x,y,keys in zip(x,y,keys):
    print("%.4f" % x, "%.4f" % y, keys)
    cutoff -= 1
    if cutoff <= 0:
        break
