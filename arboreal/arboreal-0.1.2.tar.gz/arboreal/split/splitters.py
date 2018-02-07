from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from builtins import range

import pandas as pd

from arboreal.split import Split
from arboreal.impurity import information_gain
from arboreal.dtypes import ORDERED_DTYPES, NUMERICAL_DTYPES


def split_ordered_manual(data, feature, label, split_point):
    assert isinstance(data, pd.DataFrame)
    assert str(data[feature].dtype) in ORDERED_DTYPES
    missing_index = data[feature].isnull()
    left_index = data[feature] < split_point
    right_index = data[feature] >= split_point
    left_index[missing_index] = False
    right_index[missing_index] = False
    split = Split(left_index=left_index,
                  right_index=right_index,
                  missing_index=missing_index,
                  feature=feature,
                  split_point=split_point,
                  split_types=['MANUAL', 'ORDERED'],
                  impurity_f=None, gains=None, impuritys=None)
    return split


def split_numerical(data, feature, label, impurity_f):
    assert isinstance(data, pd.DataFrame)
    assert str(data[feature].dtype) in NUMERICAL_DTYPES
    missing_index = data[feature].isnull()
    not_missing_index = ~missing_index
    split_points = set(data[feature][not_missing_index])
    gains = {}
    impuritys = {}
    impurity_all = impurity_f(data[label][not_missing_index])
    labels_all = data[label][not_missing_index]
    for split_point in split_points:
        left_index = not_missing_index & (data[feature] < split_point)
        right_index = not_missing_index & (data[feature] >= split_point)
        labels_left = data[label][left_index]
        labels_right = data[label][right_index]
        gain, impurity = information_gain(
            labels_left=labels_left,
            labels_right=labels_right,
            labels_all=labels_all,
            impurity_f=impurity_f,
            impurity_all=impurity_all)
        gains[split_point] = gain
        impuritys[split_point] = impurity
    split_point = max(gains, key=lambda x: gains[x])
    left_index = not_missing_index & (data[feature] < split_point)
    right_index = not_missing_index & (data[feature] >= split_point)
    split = Split(left_index=left_index,
                  right_index=right_index,
                  missing_index=missing_index,
                  feature=feature,
                  split_point=split_point,
                  split_types=['NUMERICAL'],
                  impurity_f=impurity_f,
                  gains=gains, impuritys=impuritys)
    return split
