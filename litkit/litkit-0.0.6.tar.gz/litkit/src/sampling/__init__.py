from itertools import chain, combinations


def powerset(iterable):
    s = list(iterable)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))

    return [list(x) for x in ps]