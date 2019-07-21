# theseus_node

## Install
pip install theseus

## Sample usage
```python
import theseus as th
import sys

_ratio=float(sys.argv[1])
_uniquify=eval(sys.argv[2])
if not isinstance(_uniquify, bool):
    print("second flag must be True/False")

n_casko = th.Node()
n_casko.load_file('tests/data/poe/poe_cask_of_amontillado.txt', uniquify=_uniquify)

n_raven = th.Node()
n_raven.load_file('tests/data/poe/poe_raven.txt', uniquify=_uniquify)


n_backg = th.Node()
n_backg.load_file('tests/data/poe/poe_cask_of_amontillado.txt', uniquify=_uniquify)
n_backg.load_file('tests/data/poe/poe_raven.txt', uniquify=_uniquify)

x, y, keys = n_casko.create_xy_table(n_backg, ratio=_ratio)

print("Cask of amontillado against background")
n_casko.show_top(n_backg, cutoff=10, ratio=_ratio)
print()
print("The Raven against background")
n_raven.show_top(n_backg, cutoff=10, ratio=_ratio)
```
