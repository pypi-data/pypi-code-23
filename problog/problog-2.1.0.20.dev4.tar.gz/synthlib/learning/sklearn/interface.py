from synthlib.data import Table, TransformedTable
from synthlib.utils import AbstractMethod
from synthlib.data.numpy import NumpyTable, table_to_numpy
import numpy


class ToolInterface(object):

    def to_classifier(self, data, target, algorithm=None):
        raise AbstractMethod()


class SKLearnInterface(ToolInterface):

    def __init__(self):
        pass

    def to_classifier(self, data, target, algorithm=None):
        """Transform the data into a format suitable for sklearn classification.

        :param data: original data
        :type data: Table
        :param target: target column
        :type target: int
        :param algorithm: classification algorithm that will be used
        :type algorithm: str
        :return: transformed table
        :rtype: SKLearnTargetData
        """
        class_labels = None
        tr = TransformedTable(data)
        for c, ft in enumerate(data.column_types):
            tr.append_columns(ft.to_numeric(c == target), c)
            if c == target:
                class_labels = ft.values
        target_new = tr.find_column(target)
        assert len(target_new) == 1
        target_new = target_new[0]
        return SKLearnTargetData(tr, target_new, class_labels)


class SKLearnTargetData(object):

    def __init__(self, data, target, class_labels=None):
        """

        :param data:
        :type data: TransformedTable
        :param target:
        """
        self._data = data
        self._target = target
        self._class_labels = class_labels

    def encode(self, data=None):
        ci = self._data.column_index
        if data is None:
            x = table_to_numpy(self._data[:, ci[:self._target] + ci[self._target+1:]])
            y = table_to_numpy(self._data[:, self._target])
            return x, y
        else:
            tr = self._data.apply(data)
            x = table_to_numpy(tr[:, ci[:self._target] + ci[self._target+1:]])
            y = table_to_numpy(tr[:, self._target])
            return x, y

    def decode(self, x, y):
        if x is None:
            x = numpy.zeros((y.shape[0], self._data.column_count - 1))

        if len(y.shape) == 1:
            y = y.reshape(-1, 1)

        base = NumpyTable(numpy.hstack((x, y)))
        return self._data.invert(base)

    @property
    def column_names(self):
        return self._data.column_names

    @property
    def class_names(self):
        return self._class_labels
