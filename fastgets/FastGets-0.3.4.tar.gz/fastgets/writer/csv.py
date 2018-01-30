import csv
from .base import Writer


class CsvWriter(Writer):

    def save(self):
        with open(self._path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(self._columns)
            writer.writerows(self._data)