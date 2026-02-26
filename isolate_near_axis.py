import math
import matplotlib.pyplot as plt

def isolate_words_near_axis(x, y, words, degrees=10, axis="x", plot=True, figsize=(10, 8)):
    """
    Isolate words whose (x, y) points lie within ±degrees of a chosen axis.

    Interpretation:
      - Near x-axis => small |angle from x-axis| => y is small relative to x
      - Near y-axis => small |angle from y-axis| => x is small relative to y

    Parameters
    ----------
    x, y : list/array-like of numbers
    words : list of str
    degrees : float
        Angular threshold in degrees (e.g., 10 means within ±10° of the axis).
    axis : {"x", "y", "either"}
        Which axis proximity to test.
        - "x": near x-axis
        - "y": near y-axis
        - "either": near x-axis OR near y-axis
    plot : bool
        If True, make a plot of only the isolated words.
    figsize : tuple
        Figure size if plotting.

    Returns
    -------
    selected : list of tuples
        [(xi, yi, word), ...] for the points that matched.
    """
    if not (len(x) == len(y) == len(words)):
        raise ValueError("x, y, and words must be the same length.")

    theta = math.radians(degrees)
    selected = []

    for xi, yi, w in zip(x, y, words):
        # Skip the origin (angle undefined, and it's not informative here)
        if xi == 0 and yi == 0:
            continue

        # Angle from x-axis: atan2(|y|, |x|)
        ang_from_x = math.atan2(abs(yi), abs(xi))  # in [0, pi/2]
        # Angle from y-axis: atan2(|x|, |y|)
        ang_from_y = math.atan2(abs(xi), abs(yi))  # in [0, pi/2]

        near_x = ang_from_x <= theta
        near_y = ang_from_y <= theta

        if axis == "x" and near_x:
            selected.append((xi, yi, w))
        elif axis == "y" and near_y:
            selected.append((xi, yi, w))
        elif axis == "either" and (near_x or near_y):
            selected.append((xi, yi, w))
        elif axis not in {"x", "y", "either"}:
            raise ValueError('axis must be one of {"x", "y", "either"}')

    if plot:
        plt.figure(figsize=figsize)
        xs = [p[0] for p in selected]
        ys = [p[1] for p in selected]
        ws = [p[2] for p in selected]

        plt.scatter(xs, ys)
        for xi, yi, w in selected:
            print(w)
            plt.text(xi, yi, w, fontsize=9, ha="right", va="bottom")

        plt.axhline(0, linewidth=1)
        plt.axvline(0, linewidth=1)
        plt.grid(True)
        plt.title(f'Words within ±{degrees}° of {axis}-axis' if axis != "either"
                  else f'Words within ±{degrees}° of x- or y-axis')
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.show()

    return selected