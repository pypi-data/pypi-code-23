#!/usr/bin/env python3

"""Classes and functions related to n-grams.
"""

import doctest

from enforsml.text import utils, bagofwords


class NGram(object):
    """The ngram class stores an n-gram.

    Given a list of Words, an n-gram is created. If a list of two Words
    is provided, a bi-gram is created. If three Words are provided, a
    3-gram is created, and so on.

    >>> from enforsml.text.word import *
    >>> word1 = Word("some")
    >>> word2 = Word("words")
    >>> bi_gram = NGram([word1, word2])
    >>> bi_gram
    NGram([Word('some', word_type=1), Word('words', word_type=1)])
    >>> print(bi_gram)
    some words
    >>> len(bi_gram)
    2

    We can also do comparisons:

    >>> word1 = Word("one")
    >>> word2 = Word("two")
    >>> word3 = Word("one")
    >>> ngram1 = NGram([word1, word2])
    >>> ngram2 = NGram([word3, word2])
    >>> ngram1 == ngram2
    True
    >>> ngram3 = NGram([word1, word2, word3])
    >>> ngram1 == ngram3
    False

    We can check if one ngram is a subset of another:

    >>> word1 = Word("one")
    >>> word2 = Word("two")
    >>> word3 = Word("three")
    >>> word4 = Word("four")
    >>> ngram1 = NGram([word1, word2, word3])
    >>> ngram1 in ngram1
    True
    >>> ngram2 = NGram([word1, word2])
    >>> ngram1 in ngram2
    False
    >>> ngram2 in ngram1
    True
    >>> ngram3 = NGram([word1, word3])
    >>> ngram3 in ngram1
    False
    >>> ngram4 = NGram([word2])
    >>> ngram4 in ngram1
    True
    >>> ngram5 = NGram([word4])
    >>> ngram5 in ngram1
    False

    It is also possible to subtract one ngram from another:

    >>> word1 = Word("one")
    >>> word2 = Word("two")
    >>> word3 = Word("three")
    >>> ngram1 = NGram([word1, word2, word3])
    >>> ngram2 = NGram([word2])
    >>> ngram1 - ngram2
    NGram([Word('one', word_type=1), Word('three', word_type=1)])
    >>> ngram3 = NGram([word1])
    >>> ngram1 - ngram3
    NGram([Word('two', word_type=1), Word('three', word_type=1)])
    >>> ngram1 - ngram1
    NGram([])
    >>> ngram1 - NGram([word2, word3])
    NGram([Word('one', word_type=1)])
    """

    def __init__(self, words):
        if not words:
            self.words = []
        else:
            self.words = words

    def __len__(self):
        return len(self.words)

    def __repr__(self):
        return "NGram(%s)" % self.words

    def __str__(self):
        output = ""

        for word in self.words:
            output = output + str(word) + " "

        return output.strip()

    def __eq__(self, other_ngram):
        if len(self) != len(other_ngram):
            return False

        for i in range(0, len(self.words)):
            if self.words[i] != other_ngram.words[i]:
                return False

        return True

    def __sub__(self, other_ngram):
        new_ngram_words = []

        index = self.subset_index(other_ngram)

        if index < 0:
            return []

        new_ngram_words = self.words[0:index]
        subset_end = index + len(other_ngram)

        if subset_end < len(self):
            new_ngram_words.extend(self.words[subset_end:])

        return NGram(new_ngram_words)

    def subset_index(self, other_ngram):
        i, j = 0, 0
        index = -1

        while i < len(self.words) and j < len(other_ngram.words):
            if self.words[i] == other_ngram.words[j]:
                if index < 0:
                    index = i
                j += 1
            elif j > 0:
                return -1
            i += 1

        if j == len(other_ngram.words):
            return index
        else:
            return -1

    def __contains__(self, other_ngram):
        return self.subset_index(other_ngram) > -1


class NGramMatrix(object):
    """A list of dicts, where each dict will hold NGrams.
    """

    def __init__(self, min_n, max_n):
        self.min_n = min_n
        self.max_n = max_n
        self.matrix = []

        for n in range(0, max_n + 1):
            self.matrix.append({})

    def add_sentence_value(self, sentence, value):
        """Add a value to a sentence, and all its ngrams.
        """

        for n in range(self.min_n, self.max_n + 1):
            ngrams = make_ngrams(utils.split_sentence(sentence), n)

            for ngram in ngrams:
                dict_key = str(ngram)

                try:
                    ngram_values = self.matrix[n][dict_key]
                except KeyError:
                    ngram_values = []

                ngram_values.append(value)
                self.matrix[n][dict_key] = ngram_values


    def get_sentence_avg_value(self, sentence):
        """Get the average value for a sentence.
        """

        all_values = self.get_sentence_values(sentence)

        try:
            avg = sum(all_values) / len(all_values)
        except ZeroDivisionError:
            avg = 0

        return avg

    def get_sentence_values(self, sentence):
        """Get all the values for a sentence.
        """

        all_values = []

        for n in range(self.min_n, self.max_n + 1):
            ngrams = make_ngrams(utils.split_sentence(sentence), n)

            for ngram in ngrams:
                dict_key = str(ngram)
                value_sum = 0

                try:
                    values = self.matrix[n][dict_key]
                    for value in values:
                        value_sum = value_sum + value

                        avg = value_sum / len(values)

                    # Multiply the average, to weigh it.
                    # 3-gram matches are three times more significant than
                    # unigram matches.
                    all_values.append(avg * pow(1.5, n - 1))
                except KeyError:
                    pass  # This ngram didn't exist

        return all_values


class WeightedNGramDict(object):
    """A dictionary where each NGram hold only one value - a weight.
    """

    def __init__(self, corpus, train_sentences):
        self.weights = {}
        sub_corpus = bagofwords.BagOfWords()
        
        for sentence in train_sentences:
            sub_corpus.add_words(sentence.lower().split(" "))

        self.weights = corpus.tfidf(sub_corpus)

    def __str__(self):
        output = "WeightedNGramDict\n================\n"

        for word in self.weights.keys():
            output += "%s: %s\n" % (word, self.weights[word])

        return output.strip()
        
    def get_sentence_weight(self, sentence):
        """Return the sum of the weights for all the words in the sentence.
        """

        total_weight = 0

        for word in sentence.split(" "):
            try:
                total_weight += self.weights[word]
            except KeyError:
                pass

        return total_weight

def make_ngrams(words, n):
    """Return n-grams from a list of Words.
    """

    num_words = len(words)
    index = 0
    n_grams = []

    while index + n <= num_words:
        n_gram = NGram(words[index:index + n])
        n_grams.append(n_gram)
        index = index + 1

    return n_grams


def run_doctests():
    doctest.testmod()
