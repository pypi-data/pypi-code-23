from schemapy.exceptions import ResponseError
from addict import Dict

from collections import Iterable, Mapping


class Response:
    def __init__(self, rows, fields=None):
        if isinstance(rows, str):
            raise ResponseError('rows cannot be a string')

        if not isinstance(rows, Iterable) or isinstance(rows, Mapping):
            rows = [rows]

        if fields is None:
            fields = []

        self._rows = rows
        self.fields = fields
        self._rowid = 0
        self._nrows = len(rows)

    def __repr__(self):
        return 'Response(count={0}, fields=[{1}])'.format(
            self._nrows,
            ', '.join([
                '{0}:{1}{2}'.format(
                    field.name,
                    field.type,
                    '*' if field.required else ''
                )
                for field in self.fields
            ])
        )

    def __len__(self):
        return self._nrows

    def __iter__(self):
        return self

    def __next__(self):
        if self._rowid < self._nrows:
            ret = self[self._rowid]
            self._rowid += 1
            return ret

        else:
            raise StopIteration

    def __getitem__(self, idx):
        if idx >= self._nrows:
            raise IndexError('list index out of range')

        row = self._rows[idx]

        record = Dict()

        for field in self.fields:
            if field.required and field.name not in row:
                raise ResponseError(
                    'Missing required field: {0}'.format(field.name)
                )

            if field.name in row:
                validated = field.validate(row[field.name])

                if validated[1] is not None:
                    raise ResponseError(validated[1])

                else:
                    record[field.name] = validated[0]

        return record
