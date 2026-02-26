import theseus as th
import sys

def generate_xy_data(f1, f2, _ratio, _uniquify):
    """
    _ratio is a float
    _uniquify is true false
    
        _ratio=float(sys.argv[1])
        _uniquify=eval(sys.argv[2])
        if not isinstance(_uniquify, bool):
            print("second flag must be True/False")
    """
    n_casko = th.Node()
    n_casko.load_file(f1, uniquify=_uniquify)
    
    n_raven = th.Node()
    n_raven.load_file(f2, uniquify=_uniquify)
    
    
    n_backg = th.Node()
    n_backg.load_file(f1, uniquify=_uniquify)
    n_backg.load_file(f2, uniquify=_uniquify)
    
    x, y, keys = n_casko.create_xy_table(n_backg, ratio=_ratio)
    #print("\nX:", x, "\nY:", y, "\nKEYS:", keys, "\n")
    print(f"{f1} against background")
    n_casko.show_top(n_backg, cutoff=10, ratio=_ratio)
    #print()
    print(f"{f2} against background")
    n_raven.show_top(n_backg, cutoff=10, ratio=_ratio)
    return x, y, keys
