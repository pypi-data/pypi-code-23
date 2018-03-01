from zlib import compress as _compress

from . import util


def featurize_k2(rec):
    """Compute the ngram set of a record with a kmer size of 2 and a step
    size of 1. Useful for indexing up to 300KB of search fields.

    :type rec: :class:`polymr.record.Record`

    :returns: A set of 2-character ngram bytestrings

    """
    fs = set()
    for attr in rec:
        fs.update(util.ngrams(attr.encode(), k=2, step=1))
    return fs


def featurize_k3(rec):
    """Compute the ngram set of a record with a kmer size of 3 and a step
    size of 1. Useful for indexing up to 1GB of search fields.

    :type rec: :class:`polymr.record.Record`

    :returns: A set of 3-character ngram bytestrings

    """
    fs = set()
    for attr in rec:
        fs.update(util.ngrams(attr.encode()))
    return fs


def featurize_k4(rec):
    """Compute the ngram set of a record with a kmer size of 4 and a step
    size of 1. Useful for indexing 1GB or more.

    :type rec: :class:`polymr.record.Record`

    :returns: A set of 4-character ngram bytestrings

    """
    fs = set()
    for attr in rec:
        fs.update(util.ngrams(attr.encode(), k=4, step=1))
    return fs


def featurize_compress(rec):
    """Compute the ngram set of a record with a kmer size of 3 and a step
    size of 1, but compress each record attribute with zlib. Useful
    for indexing up to 3GB of search fields.

    :type rec: :class:`polymr.record.Record`

    :returns: A set of 3-character ngram bytestrings

    """
    fs = set()
    for attr in rec:
        fs.update(util.ngrams(
            _compress(attr.encode())[2:]
        ))
    return fs


def featurize_compress_k4(rec):
    """Compute the ngram set of a record with a kmer size of 4 and a step
    size of 1, but compress each record attribute with zlib. Useful
    for indexing more than 3GB of search fields.

    :type rec: :class:`polymr.record.Record`

    :returns: A set of 4-character ngram bytestrings

    """
    fs = set()
    for attr in rec:
        fs.update(util.ngrams(
            _compress(attr.encode())[2:],
            k=4, step=1
        ))
    return fs


all = dict(k4=featurize_k4,
           k3=featurize_k3,
           k2=featurize_k2,
           compress=featurize_compress,
           compress_k4=featurize_compress_k4,
           default=featurize_compress)
