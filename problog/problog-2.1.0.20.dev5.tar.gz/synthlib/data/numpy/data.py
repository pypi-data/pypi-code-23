import numpy
from synthlib.data import Table


class NumpyTable(Table):

    def __init__(self, array):
        super(NumpyTable, self).__init__()
        self._array = array

    @property
    def row_count(self):
        return self._array.shape[0]

    @property
    def column_count(self):
        return self._array.shape[1]

    def cell(self, r, c):
        return self._array[r, c]

    def row(self, r, c_min=None, c_max=None):
        c_min, c_max = self.c_min_max(c_min, c_max)
        return self._array[r, c_min:c_max+1]

    def column(self, c, r_min=None, r_max=None):
        r_min, r_max = self.r_min_max(r_min, r_max)
        return self._array[r_min:r_max + 1, c]


def table_to_numpy(table):
    return numpy.array([list(r) for r in table.iter_rows()])
