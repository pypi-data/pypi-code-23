from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from builtins import range

import pandas as pd

from arboreal.split import Split


class Node(object):
    def __init__(self, data, features, label, parent=None, name=None):
        # Data related attributes
        assert isinstance(data, pd.DataFrame)
        assert all([feature in data.columns for feature in features])
        assert not any(data[label].isnull())
        self.features = list(features)
        self.data = data
        self.label = label

        # Tree related attributes
        assert (parent is None) or isinstance(parent, Node)
        self.parent = parent
        self.name = name
        self.split = None
        self.left = None
        self.right = None
        self.missing = None

    def is_leaf(self):
        return (self.left is None) and \
               (self.right is None) and \
               (self.missing is None) and \
               (self.split is None)

    def children(self):
        output = {}
        if self.left is not None:
            output['left'] = self.left
        if self.right is not None:
            output['right'] = self.right
        if self.missing is not None:
            output['missing'] = self.missing
        return output

    def __str__(self):
        output = ('{class_name}(n_rows={n_rows}, n_cols={n_cols}, '
                  'n_features={n_features}, label={label}, \n     '
                  'name={name})')
        output = output.format(class_name=self.__class__.__name__,
                               n_rows=self.data.shape[0],
                               n_cols=self.data.shape[1],
                               n_features=len(self.features),
                               label=self.label,
                               name=self.name)
        return output

    def __repr__(self):
        return self.__str__()

    def perform_split(self, split):
        assert self.is_leaf()
        assert isinstance(split, Split)
        assert split.feature in self.features
        assert self.data.index.equals(split.left_index.index)
        assert self.data.index.equals(split.right_index.index)
        assert self.data.index.equals(split.missing_index.index)
        self.split = split
        if any(split.left_index):
            self.left = Node(self.data[split.left_index],
                             features=self.features,
                             label=self.label, parent=self,
                             name='{}.{}'.format(self.name, 'left'))
        else:
            self.left = None
        if any(split.right_index) > 0:
            self.right = Node(self.data[split.right_index],
                              features=self.features,
                              label=self.label, parent=self,
                              name='{}.{}'.format(self.name, 'right'))
        else:
            self.right = None
        if any(split.missing_index):
            self.missing = Node(self.data[split.missing_index],
                                features=self.features,
                                label=self.label, parent=self,
                                name='{}.{}'.format(self.name, 'missing'))
        else:
            self.missing = None

    def predict(self, method='max'):
        if method == 'max':
            # FIXME: What happens when there is a tie?
            return (self.data[self.label]
                    .value_counts(sort=True, ascending=False)
                    .index[0])
        else:
            msg = 'predict method={} is not yet implemented'.format(method)
            raise NotImplementedError(msg)


class Tree(object):
    def __init__(self, data, features, label, name=None):
        self.root = Node(data, features, label, name='root')
        self.name = name

    def __str__(self):
        output = '{class_name}(name={name})'.format(
            class_name=self.__class__.__name__,
            name=self.name)
        return output

    def __repr__(self):
        return self.__str__()

    def build_greedy_recursive(self, min_rows=2):
        pass
