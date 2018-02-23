from ..utils import slices_to_ranges, AbstractMethod


class Table(object):
    """This is a wrapper around a basic table."""

    def __init__(self):
        self._column_names = {}
        self._column_types = {}

    def set_column_name(self, c, name):
        self._column_names[c] = name

    def set_column_type(self, c, ctype):
        self._column_types[c] = ctype

    @property
    def column_names(self):
        return [self.get_column_name(c) for c in range(0, self.column_count)]

    @property
    def column_types(self):
        return [self.get_column_type(c) for c in range(0, self.column_count)]

    @column_names.setter
    def column_names(self, names):
        self._column_names = {k: v for k, v in enumerate(names)}

    @column_types.setter
    def column_types(self, types):
        self._column_types = {k: v for k, v in enumerate(types)}

    def get_column_name(self, c):
        return self._column_names.get(c)

    def get_column_type(self, c):
        return self._column_types.get(c)

    def iter_columns(self, with_index=False):
        for c in range(0, self.column_count):
            if with_index:
                yield c, self.column(c)
            else:
                yield self.column(c)

    def iter_rows(self, with_index=False):
        for r in range(0, self.row_count):
            if with_index:
                yield r, self.row(r)
            else:
                yield self.row(r)

    def iter_cells(self, with_index=False):
        for r in range(0, self.row_count):
            for c in range(0, self.column_count):
                if with_index:
                    yield r, c, self.cell(r, c)
                else:
                    yield self.cell(r, c)

    def range(self, spec):
        if not isinstance(spec, tuple):
            spec = (spec, slice(None, None))
        rows = self.row_index[spec[0]]
        columns = self.column_index[spec[1]]
        return TableSelection(self, rows, columns)

    def __getitem__(self, spec):
        return self.range(spec)

    def __str__(self):
        return '\n'.join(' | '.join('%5s' % v for v in row) for row in self.iter_rows())

    @property
    def row_index(self):
        return IndexCreator(self.row_count)

    @property
    def column_index(self):
        return IndexCreator(self.column_count)

    @property
    def row_count(self):
        raise AbstractMethod()

    @property
    def column_count(self):
        raise AbstractMethod()

    @property
    def column_range(self):
        return range(0, self.column_count)

    @property
    def row_range(self):
        return range(0, self.row_count)

    def cell(self, r, c):
        raise AbstractMethod()

    def row(self, r, c_min=None, c_max=None):
        raise AbstractMethod()

    def column(self, c, r_min=None, r_max=None):
        raise AbstractMethod()

    def __iter__(self):
        for c in self.iter_cells():
            yield c

    def coordinate_lower(self, r, c, recurse=True):
        """Translate the coordinate to the underlying table (if any).

        :param r: row
        :param c: column
        :param recurse: translate recursively
        :return: tuple row/column in underlying table
        """
        return r, c

    def c_min_max(self, c_min=None, c_max=None):
        if c_min is None:
            c_min = 0
        if c_max is None:
            c_max = self.column_count - 1
        return c_min, c_max

    def r_min_max(self, r_min=None, r_max=None):
        if r_min is None:
            r_min = 0
        if r_max is None:
            r_max = self.row_count - 1
        return r_min, r_max


class DerivedTable(Table):

    def __init__(self, base):
        super(DerivedTable, self).__init__()
        self._base = base

    @property
    def base_table(self):
        return self._base

    def get_column_name(self, c):
        v = super(DerivedTable, self).get_column_name(c)
        if v is None:
            r, c = self.coordinate_lower(None, c)
            v = self._base.get_column_name(c)
        return v

    def get_column_type(self, c):
        v = super(DerivedTable, self).get_column_type(c)
        if v is None:
            r, c = self.coordinate_lower(None, c)
            v = self._base.get_column_type(c)
        return v

    def cell(self, r, c):
        return self.base_table.cell(*self.coordinate_lower(r, c, recurse=False))

    def row(self, r, c_min=None, c_max=None):
        base_r, _ = self.coordinate_lower(r, None, recurse=False)
        c_min, c_max = self.c_min_max(c_min, c_max)

        base_row = list(self.base_table.row(base_r))
        for c in range(c_min, c_max + 1):
            _, base_c = self.coordinate_lower(None, c, recurse=False)
            yield base_row[base_c]

    def column(self, c, r_min=None, r_max=None):
        _, base_c = self.coordinate_lower(c, None, recurse=False)
        r_min, r_max = self.r_min_max(r_min, r_max)

        base_column = list(self.base_table.column(base_c))
        for r in range(r_min, r_max + 1):
            base_r, _ = self.coordinate_lower(r, _, recurse=False)
            yield base_column[base_r]


class TableSelection(DerivedTable):
    """Represents a subtable consisting of an arbitrary selection of rows and columns."""

    def __init__(self, base, rows=None, columns=None):
        super(TableSelection, self).__init__(base)
        if rows is None:
            rows = list(self.base_table.row_range)
        if columns is None:
            columns = list(self.base_table.column_range)
        self._rows = rows
        self._columns = columns

    @property
    def row_count(self):
        return len(self._rows)

    @property
    def column_count(self):
        return len(self._columns)

    def coordinate_lower(self, r, c, recurse=True):
        if r is not None:
            r = self._rows[r]
        if c is not None:
            c = self._columns[c]
        if recurse:
            return self.base_table.coordinate_lower(r, c)
        else:
            return r, c


class IndexCreator(object):

    def __init__(self, length):
        self._length = length

    def __getitem__(self, r):
        if isinstance(r, slice):
            r = range(*r.indices(self._length))
        elif isinstance(r, int):
            if r == -1:
                r = range(*slice(r, None, 1).indices(self._length))
            else:
                r = range(*slice(r, r + 1, 1).indices(self._length))
        return list(r)


class TableRange(DerivedTable):
    """Represents a part of a Table."""

    def __init__(self, base, r_min=None, r_max=None, c_min=None, c_max=None):
        """

        :param base:
        :type base: Table
        :param r_min:
        :type r_min: int
        :param r_max:
        :type r_max: int
        :param c_min:
        :type c_min: int
        :param c_max:
        :type c_max: int
        """
        super(TableRange, self).__init__(base)
        self._r_min = r_min if r_min is not None else 0
        self._r_max = r_max if r_max is not None else self.base_table.row_count - 1
        self._c_min = c_min if c_min is not None else 0
        self._c_max = c_max if c_max is not None else self.base_table.column_count - 1

    def _in_range(self, r, c):
        return (r is None or 0 <= r <= self.row_count) and (c is None or 0 <= c <= self.column_count)

    def coordinate_lower(self, r, c, recurse=True):
        if not self._in_range(r, c):
            raise IndexError('Coordinate out of range!')
        if r is None:
            r_out = None
        else:
            r_out = r + self._r_min
        if c is None:
            c_out = None
        else:
            c_out = c + self._c_min
        if recurse:
            return self.base_table.coordinate_lower(r_out, c_out, recurse=True)
        else:
            return r_out, c_out

    @property
    def row_count(self):
        return self._r_max - self._r_min + 1

    @property
    def column_count(self):
        return self._c_max - self._c_min + 1

    def row(self, r, c_min=None, c_max=None):
        r, c = self.coordinate_lower(r, None, recurse=False)
        if not self._in_range(None, c_min) or not self._in_range(None, c_max):
            raise IndexError('Coordinate out of range!')
        if c_min is None:
            c_min = self._c_min
        else:
            c_min += self._c_min
        if c_max is None:
            c_max = self._c_max
        else:
            c_max += self._c_min
        return self.base_table.row(r, c_min=c_min, c_max=c_max)

    def column(self, c, r_min=None, r_max=None):
        r, c = self.coordinate_lower(None, c, recurse=False)
        if not self._in_range(r_min, None) or not self._in_range(r_max, None):
            raise IndexError('Coordinate out of range!')
        if r_min is None:
            r_min = self._r_min
        else:
            r_min += self._r_min
        if r_max is None:
            r_max = self._r_max
        else:
            r_max += self._r_min
        return self.base_table.column(c, r_min=r_min, r_max=r_max)
