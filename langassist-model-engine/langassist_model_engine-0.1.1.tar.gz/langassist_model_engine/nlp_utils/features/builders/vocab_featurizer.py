import logging
from time import time

import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer

from langassist_model_engine.nlp_utils.features import sentence_features
from langassist_model_engine.nlp_utils.features.builders.base import BaseFeaturizer

logger = logging.getLogger(__name__)

class VocabFeaturizer(BaseFeaturizer):
    '''
    This class will turn a piece of text into a vocabulary-dependent set of features

    `data_df` is the pandas DataFrame which will be used to construct the vocabulary.
    It should have the form

                document            l1
                "some text"         KOR
                "more text"         ESP
                ...                 ...

    The text in the `document` column is used to construct a vocabulary of ngram features for
    both characters and words.
    The vocabulary will be used to construct a vector whose length is the sum of the lengths of
    all the ngram vocabularies for that type {char, word}
    '''
    def __init__(self, data_df, word_range, char_range):
        BaseFeaturizer.__init__(self)
        self.word_range = word_range
        self.char_range = char_range
        self.word_pres_vec, self.char_count_vec = self.build_vocabs(data_df)


    def build_vocabs(self, df_data):
        '''
        Use the dataframe to construct a `CountVectorizer` for char ngrams, and
        word-presence `CountVectorizer` for words.
        :param df_data:
        :return:
        '''
        logger.info("Building CountVectorizers")
        vocab_vect_word = CountVectorizer(ngram_range=self.word_range, binary=True)
        vocab_vect_word.fit_transform(df_data['document'])
        vocab_word = vocab_vect_word.vocabulary_

        word_pres_vec = CountVectorizer(ngram_range=self.word_range,
                                        vocabulary=vocab_word)

        vocab_vect_char = CountVectorizer(ngram_range=self.char_range, analyzer='char')
        vocab_vect_char.fit_transform(df_data['document'])
        vocab_char = vocab_vect_char.vocabulary_

        char_count_vec = CountVectorizer(ngram_range=self.char_range,
                                              vocabulary=vocab_char, analyzer='char', binary=False)

        del vocab_vect_word
        del vocab_vect_char

        return word_pres_vec, char_count_vec

    def featurize(self, text):
        s_feats = sentence_features.build_sentence_features(text)
        char_counts = self.count_chars(text)
        word_presence = self.word_presence(text)

        ngram_features = np.concatenate((word_presence, char_counts))
        total_features = np.insert(ngram_features, 0, list(s_feats))

        return sparse.csr_matrix(total_features)


    def featurize_all(self, samples):
        '''
            Turn all samples into features.
            Samples is expected as a pandas DataFrame
        :param samples:
        :return:
        '''
        logger.info("Building Features...")
        t0 = time()

        vf = np.vectorize(lambda s: self.featurize(s))

        s_features = vf(samples)
        logger.debug("Done in %0.3fs" % (time() - t0))

        return sparse.vstack(s_features)


    def count_chars(self, text):
        '''
        Generate the ngram count vector, which is a vector of real values indicating
        the count of a char ngram in the sample text
        :param data:
        :return:
        '''
        return self.char_count_vec.fit_transform([text]).toarray()[0]


    def word_presence(self, text):
        '''
        Generate the word_presence_vector, which is a V long vector of binary values indicating
        whether or not a word is present
        :param text_col:
        :return:
        '''
        return self.word_pres_vec.fit_transform([text]).toarray()[0]