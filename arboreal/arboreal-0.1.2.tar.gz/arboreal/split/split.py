from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from builtins import range

import pandas as pd


class Split(object):
    def __init__(self, left_index, right_index, missing_index,
                 feature, split_point, split_types, impurity_f,
                 gains, impuritys):
        assert isinstance(left_index, pd.Series)
        assert isinstance(right_index, pd.Series)
        assert isinstance(missing_index, pd.Series)
        assert not any(left_index & right_index)
        assert not any(left_index & missing_index)
        assert not any(right_index & missing_index)

        self.left_index = left_index
        self.right_index = right_index
        self.missing_index = missing_index
        self.feature = feature
        self.split_point = split_point
        self.split_types = split_types
        self.impurity_f = impurity_f
        self.gains = gains
        self.impuritys = impuritys
