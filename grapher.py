import matplotlib.pyplot as plt

def plot_words_xy(x, y, words, n=None, figsize=(10, 8)):
    """
    Plot words at their (x, y) coordinates.

    Parameters:
    -----------
    x : list or array-like
        X coordinates
    y : list or array-like
        Y coordinates
    words : list of str
        Words corresponding to coordinates
    n : int, optional
        Number of words to display (default: all)
    figsize : tuple
        Figure size
    """

    # Basic sanity check
    if not (len(x) == len(y) == len(words)):
        raise ValueError("x, y, and words must be the same length.")

    # Limit number of points if requested
    if n is not None:
        x = x[:n]
        y = y[:n]
        words = words[:n]

    plt.figure(figsize=figsize)

    # Scatter plot
    plt.scatter(x, y)

    # Add word labels
    for xi, yi, word in zip(x, y, words):
        plt.text(xi, yi, word, fontsize=9, ha='right', va='bottom')

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Word Embedding Visualization")
    plt.grid(True)

    plt.show()