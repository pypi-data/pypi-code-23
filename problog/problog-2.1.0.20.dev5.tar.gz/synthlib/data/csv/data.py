import csv
from synthlib.data import Table


class CSVTable(Table):

    def __init__(self, filename, with_header=True, **options):
        super(CSVTable, self).__init__()
        self._filename = filename

        with open(self._filename) as f:
            data = list(csv.reader(f, **options))

        self.__column_count = len(data[0])
        if with_header:
            self.column_names = data[0]
            self._data = data[1:]
        else:
            self._data = data

    @property
    def row_count(self):
        return len(self._data)

    @property
    def column_count(self):
        return self.__column_count

    def cell(self, r, c):
        return self._data[r][c]

    def row(self, r, c_min=None, c_max=None):
        c_min, c_max = self.c_min_max(c_min, c_max)
        return self._data[r][c_min:c_max+1]

    def column(self, c, r_min=None, r_max=None):
        r_min, r_max = self.r_min_max(r_min, r_max)
        for r in range(r_min, r_max+1):
            yield self._data[r][c]
