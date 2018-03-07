from .. import Table
from .. import CategoricalField, NumericalField, StringField, DateTimeField


class ARFFTable(Table):

    def __init__(self, filename):
        super(ARFFTable, self).__init__()
        self._filename = filename

        with open(self._filename) as f:
            columns = self.read_header(f)
            self.__column_count = len(columns)
            self.column_names, self.column_types = zip(*columns)
            self._data = self.read_data(f, self.__column_count)

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

    @classmethod
    def read_header(cls, data):
        columns = []
        for line in data:
            line = line.strip()
            if line.lower().startswith('@data'):
                # end of header reached
                return columns
            elif line.lower().startswith('@attribute'):
                attr, name, dtype_str = line.split(None, 2)
                dtype = cls.parse_typestr(dtype_str)
                columns.append((name, dtype))
        raise ValueError('Unexpected end-of-file')

    @classmethod
    def parse_typestr(cls, typestr):
        typestr = typestr.strip()
        if typestr.startswith('{') and typestr.endswith('}'):
            values = list(safe_split(',', typestr[1:-1]))
            return CategoricalField(values)
        elif typestr.lower() in ('numeric', 'real', 'integer'):
            return NumericalField()
        elif typestr.lower() in ('string', ):
            return StringField()
        elif typestr.lower().startswith('date'):
            parts = typestr.split(None, 1)
            if len(parts) > 1:
                return DateTimeField(parts[1])
            else:
                return DateTimeField()
        else:
            raise ValueError('Unsupported ARFF data type: \'%s\'' % typestr)

    @classmethod
    def read_data(cls, data, ncols=None):
        # TODO support instance weights (lines end with {W})
        result = []
        for line in data:
            line = line.strip()
            if line:
                if line.startswith('{'):
                    # sparse format
                    values = [0] * ncols
                    for val in safe_split(',', line[1:-1]):
                        i, v = val.split(None, 1)
                        values[int(i) - 1] = v
                else:
                    values = list(safe_split(',', line))
                    if ncols is not None and len(values) != ncols:
                        raise ValueError('Unexpected number of values!')
                    result.append(values)
        return result


def safe_split(splitchar, string, strip=True):
    """Split a string on a given character, ignored those enclosed in single quotes.

    :param splitchar: character to split on
    :type splitchar: str
    :param string: string to split
    :type string: str
    :param strip: strip whitespace from extracted pieces [default: True]
    :type strip: bool
    :return: generator of pieces
    :rtype: generator<str>
    """
    assert len(splitchar) == 1
    in_quote = False
    s = 0
    for i, c in enumerate(string):
        if c == "'":
            in_quote = not in_quote
        elif not in_quote and c == splitchar:
            if strip:
                yield string[s:i].strip()
            else:
                yield string[s:i]
            s = i + 1
    yield string[s:]

