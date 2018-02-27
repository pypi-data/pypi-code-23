# -*- coding: utf-8 -*-
"""Functions to count the words co-occurrence within a corpus.

This module provides the main function count_cooccurrence to construct a CountBasedRepresentation.
"""
import collections
import logging
import math
import multiprocessing
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
def count_cooccurrence(corpus, words,
                       context=mangoes.context.Window(),
                       subsampling=False, nb_workers=None):
    """Build a CountBasedRepresentation where rows are the words in `words`, counting co-occurrences from the `corpus`.

    Examples
    --------
    >>> import mangoes.counting
    >>> window_5 = mangoes.context.Window(window_half_size=5)
    >>> counts_matrix = mangoes.counting.count_cooccurrence(corpus, vocabulary, context=window_5)

    Parameters
    -----------
    corpus: mangoes.Corpus
    words: mangoes.Vocabulary
        words represented as vectors (rows of the matrix)
    context: mangoes.context.Context or mangoes.Vocabulary
        A Vocabulary or context defining function such as defined in the :mod:`mangoes.context` module.
        Default is a window of size 1-x-1 : count the co-occurrences between the words in `words_vocabulary` and the
        words surrounding it.
        If `context` is a Vocabulary, only consider the words of this vocabulary in the window.
    nb_workers: int
        number of subprocess to use;
    subsampling: boolean or dict
        to apply subsampling on frequent words. Value can be False (default), True or a frequency
        threshold. If True, the default value of `create_subsampler()` function is used

    Returns
    -------
    mangoes.CountBasedRepresentation

    """
    if words is None:
        raise mangoes.utils.exceptions.RequiredValue("'words' is required to count cooccurrences")

    if isinstance(context, mangoes.Vocabulary):
        context = mangoes.context.Window(context)

    if context.vocabulary:
        features = context.vocabulary
    else:
        features = mangoes.vocabulary.DynamicVocabulary()

    if not nb_workers:
        nb_workers = multiprocessing.cpu_count() - 1

    data_parallel = mangoes.utils.multiproc.DataParallel(_count_context_cooccurrence,
                                                         _reduce_counter,
                                                         nb_workers=nb_workers)

    kwargs = {}
    if subsampling:
        kwargs['subsampler'] = create_subsampler(corpus) if subsampling is True else create_subsampler(corpus,
                                                                                                       subsampling)
    if corpus.nb_sentences:
        kwargs['nb_sentences'] = _estimate_nb_sentences_per_worker(corpus.nb_sentences, nb_workers)

    kwargs['annotated'] = corpus.is_annotated

    matrix, contexts_words = data_parallel.run(corpus,
                                               *(context, words, features),
                                               **kwargs)

    features = mangoes.Vocabulary(contexts_words)

    hyperparameters = {"corpus": corpus.params,
                       "context_definition": context.params,
                       "subsampling": subsampling}

    return mangoes.CountBasedRepresentation(words, features, matrix, hyperparameters)


def _count_context_cooccurrence(sentences, context, words_vocabulary, contexts_vocabulary,
                                nb_sentences=None, subsampler=None, annotated=False):
    """Parallelizable function to count cooccurrence

    Count cooccurrence between words and contexts as defined by the 'context_definition' function, and on the
    sentences given by the 'sentences_enumerator'.

    Parameters
    -----------
    sentences: mangoes.utils.reader.SentenceGenerator
        an iterator over sentences
    context: callable
        a context defining function such as defined in 'mangoes.context'
    words_vocabulary: mangoes.Vocabulary
        words to represent as vectors (rows of the matrix)
    contexts_vocabulary: mangoes.Vocabulary
        words to use as features (columns of the matrix)
    nb_sentences: int, optional
        number of sentences. Only used for the progress bar
    subsampler: dict, optional
        a dictionary with probabilities of removal of frequent words
    annotated: bool
        wheter or not the content in sentences is annotated

    Returns
    --------
    (collections.Counter, mangoes.Vocabulary)
    """
    rows = []
    cols = []

    filter_word_sentence = mangoes.vocabulary.create_tokens_filter(words_vocabulary.entity)
    filter_bigrams_sentence = mangoes.vocabulary.create_bigrams_filter(words_vocabulary.get_bigrams(), annotated)

    with ProgressBar(total=nb_sentences) as progress_bar:
        for sentence in sentences:
            sentence = filter_bigrams_sentence(sentence)
            if subsampler:
                sentence = _subsample(sentence, subsampler)

            word_sentence = filter_word_sentence(sentence)
            word_sentence_mask = [True if w in words_vocabulary else False for w in word_sentence]

            for position, (word, word_contexts) in enumerate(zip(word_sentence,
                                                                 context(sentence,
                                                                         mask=word_sentence_mask))):
                for context_word in word_contexts:
                    if word_sentence_mask[position]:
                        rows.append(words_vocabulary.index(word))
                        cols.append(contexts_vocabulary.index(context_word))

            progress_bar.update()

    csr = sparse.csr_matrix(([1] * len(rows), (rows, cols)),
                            shape=(len(words_vocabulary), len(contexts_vocabulary)))
    return csr, contexts_vocabulary


def _reduce_counter(total, part):
    total_counter, total_vocabulary = total
    part_counter, part_vocabulary = part

    if total_vocabulary == part_vocabulary:
        return total_counter + part_counter, total_vocabulary

    part_to_total_indices_map = {index_in_part: total_vocabulary.index(word)
                                 for index_in_part, word in enumerate(part_vocabulary)}
    # during the mapping, words of part_vocabulary are added to total_vocabulary

    new_shape = (total_counter.shape[0], len(total_vocabulary))

    # update the indices in part_counter to map them to total_counter
    new_indices = np.array([part_to_total_indices_map[i] for i in part_counter.indices])
    new_part = sparse.csr_matrix((part_counter.data, new_indices, part_counter.indptr), shape=new_shape)

    # reshape total
    total_counter = sparse.csr_matrix((total_counter.data, total_counter.indices, total_counter.indptr),
                                      shape=new_shape)

    return total_counter + new_part, total_vocabulary


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


def _estimate_nb_sentences_per_worker(nb_sentences, nb_workers):
    if nb_workers > 1:
        return nb_sentences // (nb_workers - 1)
    return nb_sentences
