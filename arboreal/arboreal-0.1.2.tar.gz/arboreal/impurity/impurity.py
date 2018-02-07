from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from builtins import range

import pandas as pd
import numpy as np


def gini(labels):
    assert isinstance(labels, pd.Series)
    assert not any(labels.isnull())
    counts = labels.value_counts(sort=True, ascending=False)
    fractions = counts / float(len(labels))
    return (1 - np.sum(fractions.values ** 2))


def information_gain(labels_left, labels_right, labels_all, impurity_f,
                     impurity_all=None):
    n_left = len(labels_left)
    n_right = len(labels_right)
    n_all = len(labels_all)
    assert (n_left + n_right) == n_all
    impurity = {}
    if impurity_all is None:
        impurity['all'] = impurity_f(labels_all)
    else:
        impurity['all'] = impurity_all
    impurity['left'] = impurity_f(labels_left)
    impurity['right'] = impurity_f(labels_right)
    gain = impurity['all'] \
        - (n_left * float(impurity['left']) / n_all) \
        - (n_right * float(impurity['right']) / n_all)
    return gain, impurity
