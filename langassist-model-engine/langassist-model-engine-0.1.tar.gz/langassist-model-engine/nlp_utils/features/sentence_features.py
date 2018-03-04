import pandas as pd
from nlp_utils.tokenize import tokenize
import numpy as np
from scipy import sparse

import logging

logger = logging.getLogger(__name__)

'''
Features:
    - Num tokens
    - Average word length
    - log of the freq. of each character n-gram, normalized wrt text length.
        Smoothing term added to avoid 0 values for n-grams with 1 freq.
    - Word n-grams (presence or absence)
'''

####################################
###     Independent Features     ###
####################################
def num_tokens(text):
    return len(tokenize(text))

def average_word_len(text):
    '''
    Get the sum of the word lengths and divide by the number of words
    :param text:
    :return:
    '''
    word_list = tokenize(text)
    num_words = len(word_list)

    return sum([len(s) for s in word_list]) / num_words

def build_sentence_features(text):
    num_tok = num_tokens(text)
    avg_len = average_word_len(text)

    return (num_tok, avg_len)

##########################################
###     Total Feature Construction     ###
##########################################

def create_series(features):
    return pd.Series({'len': features[0],
                      'avg_word_len': features[1]})

def sentence_features_sparse(s_data, feature_builder):
    vf = np.vectorize(lambda s: feature_builder.featurize(s))
    s_data = s_data.ravel()
    s_features = vf(s_data)

    return sparse.vstack(s_features)
