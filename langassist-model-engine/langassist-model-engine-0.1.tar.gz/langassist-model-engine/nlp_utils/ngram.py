def build_n_grams(items, n):
    """
    This function simply splits the items into n-tuples representing n-grams.
    The * operator splits a list into a series of arguments passed to a function.
    So effectively, this function calls:
        return zip(items[1:], items[2:], ..., items[n:])

    Pass a `str` for char n-grams, or a `list` of tokens for word n-grams
    :param items:
    :param n:
    :return a list of n-tuples representing n-grams of the tokens:
    """
    return list(zip(*[items[i:] for i in range(n)]))