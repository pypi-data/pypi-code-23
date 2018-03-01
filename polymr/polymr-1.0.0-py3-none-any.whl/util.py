from itertools import chain
from heapq import merge as _merge

KMER_SIZE = 3
STEP_SIZE = 1

cat = chain.from_iterable


def avg(l):
    """Compute the arithmetic mean on a list of numbers.

    :type l: list of any numeric type

    :returns: float
    """

    return sum(l)/len(l)


def ngrams(s, k=KMER_SIZE, step=STEP_SIZE):
    """Generate a list of ngrams by sliding window. An example is probably
    best:

    .. doctest::

      >>> polymr.util.ngrams('bon jovi', 3, 1)
      ['bon', 'on ', 'n j', ' jo', 'jov', 'ovi']

    :param s: The string to break into ngrams
    :type s: str

    :keyword k: The size of each ngram to make, also known as window
      length or kmer size.
    :type k: int

    :keyword step: The step size: how many character positions to jump
      forward after each ngram.
    :type step: int

    :returns: list of str
    """

    if len(s) < k:
        return [s]
    return [s[i:i+k] for i in range(0, len(s)-k+1, step)]


def jaccard(a, b):
    """Compute the Jaccard distance between two strings.

    :type a: str

    :type b: str

    :returns: float
    """

    if not a and not b:
        return 0
    n = len(a.intersection(b))
    return 1 - (float(n) / (len(a) + len(b) - n))


def openfile(filename_or_handle, mode='r'):
    """Open a filename, or, if given a file handle, return the handle
    as-is.

    :param filename_or_handle: The file or handle to open
    :type filename_or_handle: str or file handle

    :keyword mode: The file mode c.f. Python's built-in ``open``
      function.
    :type mode: str

    :returns: open file handle

    """

    if type(filename_or_handle) is str:
        return open(filename_or_handle, mode)
    return filename_or_handle


def merge_to_range(ls):
    """Compact an iterable of integer lists into a series of ranges, where
    a range is encoded as a list of stop and end ints: [stop,
    int]. The function also returns an indicator describing whether
    any compaction was applied.

    .. doctest::

      >>> polymr.util.merge_to_range([[1,3,4,7], [2,5,8]])
      ([[1, 5], [7, 8]], True)

    """
    if hasattr(ls, "__len__") and len(ls) == 1:
        merged = iter(ls[0])
    else:
        merged = _merge(*ls)
    ret = [next(merged)]
    prev = ret[0]
    compacted = False
    for x in merged:
        if x == prev + 1:
            if type(ret[-1]) is list:
                ret[-1][-1] = x
            else:
                ret[-1] = [prev, x]
                compacted = True
        else:
            ret.append(x)
        prev = x
    return ret, compacted
