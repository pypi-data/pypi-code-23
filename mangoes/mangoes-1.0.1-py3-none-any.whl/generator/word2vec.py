# -*-coding:utf-8 -*
"""This module provides convenience functions to work with gensim's word2vec implementation

See `Gensim's website <https://radimrehurek.com/gensim/index.html>`_

.. [1] Rehurek, R., & Sojka, P. (2010). Software framework for topic modelling with large corpora. In In Proceedings
       of the LREC 2010 Workshop on New Challenges for NLP Frameworks.
.. [2] Tomas Mikolov, Kai Chen, Greg Corrado, and Jeffrey Dean. Efficient Estimation of Word Representations in
       Vector Space. In Proceedings of Workshop at ICLR, 2013.
.. [3] Tomas Mikolov, Ilya Sutskever, Kai Chen, Greg Corrado, and Jeffrey Dean. Distributed Representations of Words
       and Phrases and their Compositionality. In Proceedings of NIPS, 2013.
.. [4] Optimizing word2vec in gensim, http://radimrehurek.com/2013/09/word2vec-in-python-part-two-optimizing/

"""

import logging
import gensim.models.word2vec
from numpy import Infinity
from collections import OrderedDict
import warnings

from mangoes import Embeddings
from mangoes.vocabulary import Vocabulary
import mangoes.utils.exceptions


def create_embeddings(corpus, words_vocabulary, dimensions, window_half_size=1,
                      algorithm="sg", negative=0, subsampling=0, **kwargs):
    """Generate word embeddings using gensim's Word2Vec.

    This function will use a :class:`gensim.models.word2vec.Word2Vec` model and train it with the corpus to
    produce an :class:`.Embeddings` object.

    This function accepts the same parameters as :class:`gensim.models.word2vec.Word2Vec` except those that are
    replaced or ignored to be consistent with the other functions in mangoes and adapt to mangoes's data structures :

    * 'sentences' is replaced with 'corpus'
    * 'size' is replaced with 'dimensions'
    * 'window' is replaced with 'window_half_size'
    * 'sg' is replaced with 'algorithm'
    * 'sample' is replaced with 'subsampling'
    * 'min_count' is ignored since the vocabulary is provided
    * 'sorted_vocab' is ignored since the vocabulary is provided

    Parameters
    ----------
    corpus: mangoes.Corpus
        a corpus instance

    words_vocabulary: mangoes.Vocabulary
        the words an embedding must be learnt for

    dimensions: int
        dimensionality of the trained embedding vectors

    window_half_size: int (default = 1)
        half size of the symmetric context window around a word during training.

    algorithm: ['sg' (default), 'cbow'].
        Specify the training algorithm to use between Skip-Gram and CBOW.

    negative: int (default = 0):
        if positive, then negative sampling will be used as part of the objective function of the neural network.
        The value will then specify the number of noise word to draw (usually between 5 and 20 for small corpus,
        and between 2 and 5 for larger corpus).

    subsampling: positive float (default = 0)
        Controls downsampling of frequent words. If inferior to 1, will be interpreted as a frequency.
        If superior to 1, will be interpreted as a count value. Either way, every word whose frequency / count is
        higher than this value will be downsampled. No downsampling will be used if this value is equal to 0.

    Other Parameters
    ----------------
    kwargs
        Any parameter other parameter of :class:`gensim.models.word2vec.Word2Vec` constructor



    Returns
    -------
    an Embeddings instance
    """
    kwargs = _filter_kwargs(kwargs)

    model = gensim.models.word2vec.Word2Vec(None,
                                            size=dimensions,
                                            window=window_half_size,
                                            min_count=-Infinity,
                                            negative=negative,
                                            sg=0 if algorithm == "cbow" else 1,
                                            sample=subsampling,
                                            **kwargs)

    # Hijack Gensim's word2vec's building vocabulary step
    _fit_vocab(corpus, model, subsampling, words_vocabulary)

    try:
        model.train(corpus, total_examples=corpus.nb_sentences, epochs=model.iter)
    except TypeError:
        # gensim < 2.0
        model.train(corpus)

    hyperparameters = {"corpus": corpus.params,
                       "words": words_vocabulary.params,
                       "dimensions": dimensions,
                       "window_half_size": window_half_size,
                       "algorithm": algorithm,
                       "negative": negative,
                       "subsampling": subsampling}
    hyperparameters.update(kwargs)

    return create_embeddings_from_gensim_word2vec_model(model, hyperparameters)


def create_embeddings_from_gensim_word2vec_model(gensim_word2vec_model, hyperparameters=None):
    """Fetch the data of a trained Gensim's word2vec embedding model, and create an Embeddings instance out of them.

    Parameters
    ----------
    gensim_word2vec_model:
        trained gensim.models.word2vec.Word2Vec instance

    Returns
    -------
    an Embeddings instance
    """
    try:
        embedding_matrix = gensim_word2vec_model.wv.syn0
        words_list = gensim_word2vec_model.wv.index2word
    except AttributeError:
        # gensim < 1.0
        embedding_matrix = gensim_word2vec_model.syn0
        words_list = gensim_word2vec_model.index2word

    embedding_matrix, words_list = _remove_null_word(embedding_matrix, words_list)
    if len(embedding_matrix) == 0:
        msg = "The matrix is empty : the word2vec model may have not been trained"
        raise mangoes.utils.exceptions.IncompatibleValue(msg)

    return Embeddings(Vocabulary(words_list), embedding_matrix, hyperparameters)


def _fit_vocab(corpus, model, subsampling, words_vocabulary):
    model.corpus_count = corpus.nb_sentences

    try:
        model.build_vocab_from_freq(corpus.words_count, keep_raw_vocab=False)
    except AttributeError:
        # gensim < 3
        model.raw_vocab = {w: corpus.words_count[w] for w in words_vocabulary}

        if 0 in model.raw_vocab.values():
            words_not_in_corpus = [word for word, count in model.raw_vocab.items() if count == 0]

            msg = "The following words are not in the corpus, but Gensim's Word2Vec requires them to be. "
            msg += "You should remove them from the Vocabulary : "
            msg += "'" + "', '".join(words_not_in_corpus) + "'"

            raise mangoes.utils.exceptions.IncompatibleValue(msg=msg)
        model.scale_vocab(sample=subsampling, keep_raw_vocab=False)
        model.finalize_vocab()


def _filter_kwargs(origin_kwargs):
    replaced_kwargs = {"sentences": "corpus",
                       "size": "dimensions",
                       "window": "window_half_size",
                       "sg": "algorithm",
                       "sample": "subsampling"}
    ignored_kwargs = {"min_count": "We already chose which vocabulary to train, so we must tell Gensim's word2vec to "
                                   "keep all the words",
                      "sample": "We will manually call the 'scale_vocab()' method using the correct value",
                      "sorted_vocab": "We use our own index system since we specify ourselves which vocabulary "
                                      "to learn"}
    kept_kwargs = {}

    for arg in origin_kwargs:
        if arg in replaced_kwargs:
            msg = "'{}' parameter will be ignored and the value of '{}' parameter will be used instead"
            warnings.warn(msg.format(arg, replaced_kwargs[arg]))
        elif arg in ignored_kwargs:
            msg = "'{}' parameter will be ignored : {}"
            warnings.warn(msg.format(arg, ignored_kwargs[arg]))
        else:
            kept_kwargs[arg] = origin_kwargs[arg]

    return kept_kwargs


def _remove_null_word(embedding_matrix, words_list):
    null_word = '\0'
    if null_word in words_list:
        null_word_index = words_list.index(null_word)
        index_list = list(range(len(words_list)))
        index_list.pop(null_word_index)
        words_list.pop(null_word_index)
        embedding_matrix = embedding_matrix[index_list]
    return embedding_matrix, words_list
