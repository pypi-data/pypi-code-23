# -*- coding: utf-8 -*-
"""Functions to count the words co-occurrence within a corpus.

This module provides the main function count_cooccurrence to construct a CountBasedRepresentation.
"""
import collections
import logging
import math
import random

import numpy as np
from scipy import sparse

import mangoes.context
import mangoes.utils.decorators
import mangoes.utils.exceptions
import mangoes.utils.multiproc
from mangoes.utils.options import ProgressBar

logger = logging.getLogger(__name__)


##########
# Computing / Building a cooccurrence count instance
##########
@mangoes.utils.decorators.timer(display=logger.info)
def count_cooccurrence(corpus, words_vocabulary, contexts_vocabulary,
                       context_definition=mangoes.context.Window(), subsampling=False,
                       nb_workers=1):
    """Build a CountBasedRepresentation corresponding to the corpus, word and context vocabularies,
    and context definition.

    Examples
    --------
    >>> import mangoes.context, mangoes.counting
    >>> window_5 = mangoes.context.Window(window_half_size=5)
    >>> counts_matrix = mangoes.counting.count_cooccurrence(corpus, vocabulary, vocabulary, context_definition=window_5)

    Parameters
    -----------
    corpus: mangoes.Corpus
    words_vocabulary: mangoes.Vocabulary
        words represented as vectors (rows of the matrix)
    contexts_vocabulary: mangoes.Vocabulary
        words used as features (columns of the matrix)
    context_definition: mangoes.context.Context
        a context defining function such as defined in the :mod:`mangoes.context` module
    nb_workers: int
        number of subprocess to use;
    subsampling: boolean or dict
        to apply subsampling on frequent words. Value can be False (default), True or a frequency
        threshold. If True, the default value of `create_subsampler()` function is used

    Returns
    -------
    mangoes.CountBasedRepresentation

    """
    if words_vocabulary is None:
        raise mangoes.utils.exceptions.RequiredValue("'words' is required to count cooccurrences")
    if contexts_vocabulary is None:
        contexts_vocabulary = words_vocabulary  # TODO : le construire pendant le comptage

    word2index_map = words_vocabulary.word_index
    filter_word_sentence = _get_entity_filter(words_vocabulary.entity)

    context2index_map = contexts_vocabulary.word_index
    filter_context_sentence = _get_entity_filter(contexts_vocabulary.entity)

    data_parallel = mangoes.utils.multiproc.DataParallel(_count_context_cooccurrence,
                                                         _reduce_counter,
                                                         nb_workers=nb_workers)

    kwargs = {}

    if subsampling:
        kwargs['subsampler'] = create_subsampler(corpus) if subsampling is True else create_subsampler(corpus,
                                                                                                       subsampling)
    if corpus.nb_sentences:
        kwargs['nb_sentences'] = _estimate_nb_sentences_per_worker(corpus.nb_sentences, nb_workers)

    counter = data_parallel.run(corpus,
                                *(context_definition, word2index_map, context2index_map,
                                  filter_word_sentence, filter_context_sentence),
                                **kwargs)

    shape = (len(words_vocabulary), len(contexts_vocabulary))
    matrix = _counter_to_csr(counter, shape)

    hyperparameters = {"corpus": corpus.params,
                       "context_definition": context_definition.params,
                       "subsampling": subsampling}

    return mangoes.CountBasedRepresentation(words_vocabulary, contexts_vocabulary, matrix, hyperparameters)


@mangoes.utils.decorators.timer(display=logger.info, label="create a csr matrix from Counter")
def _counter_to_csr(counter, shape):
    """Build a sparse.csr_matrix from a collection.Counter built with count_cooccurrence.

    Parameters
    -----------
    counter: dict
        the dictionary of ((i,j), count) key-values pairs
    shape: tuple
        shape of the resulting scr matrix

    Returns
    --------
    sparse.csr_matrix
    """
    data = np.empty(shape=(len(counter), 3), dtype=np.int)
    for i, ((word_index, context_index), count) in enumerate(counter.items()):
        data[i, :] = word_index, context_index, count
    return sparse.csr_matrix((data[:, 2], (data[:, 0], data[:, 1])), shape=shape)


def _count_context_cooccurrence(sentences_enumerator, context_definition, word2index_map, context2index_map,
                                filter_word_sentence, filter_context_sentence, nb_sentences=None, subsampler=None):
    """Parallelizable function to count cooccurrence

    Count cooccurrence between words and contexts as defined by the 'context_definition' function, and on the
    sentences given by the 'sentences_enumerator'.

    Parameters
    -----------
    sentences_enumerator: mangoes.utils.reader.SentenceGenerator
        an iterator over sentences
    context_definition: callable
        a context defining function such as defined in 'mangoes.context'
    word2index_map: dict
        mapping of words and their ids
    context2index_map: dict
        mapping of contexts words and their ids.
    filter_word_sentence: callable
        if the tokens are annotated words, attributes to consider (if None (default) all attributes are considered)
    filter_context_sentence: callable
        if the tokens are annotated words, attributes to consider (if None (default) all attributes are considered)
    nb_sentences: int, optional
        number of sentences. Only used for the progress bar
    subsampler: dict, optional
        a dictionary with probabilities of removal of frequent words

    Returns
    --------
    collections.Counter
    """
    counter = collections.Counter()
    with ProgressBar(total=nb_sentences) as progress_bar:
        for sentence in sentences_enumerator:
            if subsampler:
                sentence = _subsample(sentence, subsampler)

            i_sentence = _words_to_indices(filter_context_sentence(sentence), context2index_map)
            for word_pos, word in enumerate(filter_word_sentence(sentence)):
                if word in word2index_map:
                    contexts_indices = context_definition(word_pos, i_sentence)
                    word_index = word2index_map[word]
                    counter.update((word_index, context_index) for context_index in contexts_indices)
            progress_bar.update()
    return counter


def _reduce_counter(total, part):
    total.update(part)
    return total


def _subsample(sentence, subsampler):
    return [word if word not in subsampler or random.random() > subsampler[word] else None for word in sentence]


def create_subsampler(corpus, threshold=10 ** -5):
    """Compute probabilities of removal of frequent words

    For each word appearing with a frequency higher than the threshold in the corpus, a probabilty of removal
    is computed following the formula :

    .. math::
            p = 1 - \sqrt{\\frac{t}{f}}

    where :math:`t` is the threshold and :math:`f` the frequency of the word in the corpus.

    Parameters
    ----------
    corpus: mangoes.Corpus
        Frequencies come from corpus.words_count
    threshold: float, optional
        Words appearing more than this threshold appear in the subsampler (default : :math:`10^{-5}`)

    Returns
    --------
    dict
        a dictionary associating each frequent word with a removal probability
    """
    threshold *= corpus.size
    return {word: 1 - math.sqrt(threshold / count) for word, count in corpus.words_count.items() if count > threshold}


def _get_entity_filter(entity):
    """Returns a function to filter the given entities from a sentence"""
    if entity:
        def filter_sentence(sentence):
            return [mangoes.corpus.get_attributes_from_token(token, entity) for token in sentence]
    else:
        def filter_sentence(sentence):
            return sentence
    return filter_sentence


def _words_to_indices(sentence, word2index_map):
    """Convert words to indices

    If a word isn't in word2index_map, it is replaced by -1
    :param sentence:
    :param word2index_map:
    :return: list of indices
    """
    return [word2index_map[word] if word in word2index_map else -1 for word in sentence]


def _estimate_nb_sentences_per_worker(nb_sentences, nb_workers):
    if nb_workers > 1:
        return nb_sentences // (nb_workers - 1)
    return nb_sentences
