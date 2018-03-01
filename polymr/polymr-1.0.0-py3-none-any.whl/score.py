from .util import avg
from .util import jaccard
from .util import ngrams


def features(fields):
    """Break an iterable of search fields into length-2 ngram sets.

    :type fields: iterable of str

    :returns: list of set of length-2 strs
    """
    return [set(ngrams(attr, k=2, step=1)) for attr in fields]


def hit(query_features, result_features):
    """Score a search hit. Defined as the average Jaccard distance amongst
    two ngram sets.

    :type query_features: list of set of length-2 strs
    :type result_features: list of set of length-2 strs

    :returns: float

    """
    return avg(list(map(jaccard, query_features, result_features)))
