from __future__ import print_function, division
from .table import DerivedTable, Table
from ..utils import first, list_to_slice, AbstractMethod
from collections import defaultdict
import math


class TransformedTable(DerivedTable):

    def __init__(self, base):
        super(TransformedTable, self).__init__(base)
        self._columndefs = []
        self._column_count = 0
        self._column_index = defaultdict(list)  # old -> new

    def find_column(self, old_c):
        return self._column_index[old_c]

    def get_column_name(self, c):
        v = Table.get_column_name(self, c)
        if v is None:
            col_names = []
            for tr, cols in self._columndefs:
                col_origs = [self.base_table.get_column_name(ci) for ci in cols]
                col_names += tr.label(col_origs)
            v = col_names[c]
        return v

    def append_columns(self, transform, *columns):
        self._columndefs.append((transform, columns))
        for i in range(0, transform.out_count):
            if len(columns) == 1:
                self._column_index[columns[0]].append(self._column_count + i)
        self._column_count += transform.out_count

    @property
    def row_count(self):
        return self.base_table.row_count

    @property
    def column_count(self):
        return self._column_count

    def cell(self, r, c):
        return list(self.row(r))[c]

    def row(self, r, c_min=None, c_max=None):
        outs = []
        for tr, cols in self._columndefs:
            input_d = self._base[r, cols]
            output_d = list(tr.apply(input_d))
            outs += output_d[0]
        if c_min is None:
            c_min = 0
        if c_max is None:
            return outs[c_min:]
        else:
            return outs[c_min:c_max+1]

    def column(self, c, r_min=None, r_max=None):
        raise AbstractMethod()

    def invert(self, table):
        """Apply the inverse transformations on a different table."""
        res = TransformedTable(table)
        i = 0
        for t, cs in self._columndefs:
            oc = t.out_count
            cols = range(i, i + oc)
            ti = t.invert()
            res.append_columns(ti, *cols)
            i += oc
        return res

    def apply(self, table):
        """Apply the same transformations on a different table."""
        res = TransformedTable(table)
        for t, cs in self._columndefs:
            res.append_columns(t, *cs)
        return res


class ColumnTransformation(object):

    def __init__(self, in_count, out_count):
        self._in_count = in_count
        self._out_count = out_count

    @property
    def in_count(self):
        return self._in_count

    @property
    def out_count(self):
        return self._out_count

    def apply(self, data):
        for row in data.iter_rows():
            yield self._apply_one(row)

    def _apply_one(self, value):
        raise AbstractMethod()

    def label(self, originals):
        return originals

    def invert(self):
        raise AbstractMethod()


class DummyColumnTransformation(ColumnTransformation):

    def __init__(self):
        super(DummyColumnTransformation, self).__init__(1, 1)

    def _apply_one(self, values):
        return values

    def invert(self):
        return self


class LabelEncoding(ColumnTransformation):

    def __init__(self, encode=None):
        super(LabelEncoding, self).__init__(1, 1)
        if encode is None:
            self._encode = {}
            self._decode = []
        else:
            self._encode = encode
            self._decode = []
            for k, v in self._encode.items():
                while len(self._decode) <= v:
                    self._decode.append(None)
                self._decode[v] = k

    def _apply_one(self, values):
        value = first(values)
        v = self._encode.get(value)
        if v is None:
            v = len(self._encode)
            self._encode[value] = v
            self._decode.append(value)
        return [v]

    def invert(self):
        return LabelDecoding(self._decode)


class LabelDecoding(ColumnTransformation):

    def __init__(self, decode):
        super(LabelDecoding, self).__init__(1, 1)
        self._decode = decode

    def _apply_one(self, values):
        value = first(values)
        return [self._decode[int(value)]]

    def label(self, originals):
        return originals

    def invert(self):
        encode = {v: k for k, v in self._decode.items()}
        return LabelEncoding(encode)


class OneHotEncoding(ColumnTransformation):

    def __init__(self, values):
        super(OneHotEncoding, self).__init__(1, len(values))
        self._values = values

    def _apply_one(self, values):
        value = first(values)
        result = [0] * self.out_count
        result[self._values.index(value)] = 1
        return result

    def __repr__(self):
        return '<OneHotEncoding>'

    def label(self, originals):
        return ['%s=%s' % (originals[0], v) for v in self._values]

    def invert(self):
        return CategoricalEncoding(self._values)


class CategoricalEncoding(ColumnTransformation):

    def __init__(self, values):
        super(CategoricalEncoding, self).__init__(len(values), 1)
        self._values = values

    def _apply_one(self, values):
        values = list(values)
        try:
            return [self._values[values.index(1)]]
        except ValueError:
            return [None]

    def invert(self):
        return OneHotEncoding(self._values)


class Scaling(ColumnTransformation):

    def __init__(self, offset=None, scale=None, normalize=False, parameters=None):
        super(Scaling, self).__init__(1, 1)
        self._normalize = normalize

        # Keep parameters in dictionary such that changes are propagated to the inverted model.
        if parameters is not None:
            self._parameters = parameters
        else:
            self._parameters = {'offset': offset, 'scale': scale}

    @property
    def offset(self):
        return self._parameters.get('offset')

    @offset.setter
    def offset(self, value):
        self._parameters['offset'] = value

    @property
    def scale(self):
        return self._parameters.get('scale')

    @scale.setter
    def scale(self, value):
        self._parameters['scale'] = value

    def find_parameters(self, data):
        # Parameters are not given, get them from data
        if not self._normalize:
            a, b = min(data), max(data)
            self.offset = a
            self.scale = b - a
            if self.scale < 1e-8:  # avoid 0 scaling
                self.scale = 1e-8
        else:
            self.offset, self.scale = mean_stddev(data)

    def apply(self, data):
        if self.offset is None or self.scale is None:
            self.find_parameters(data)
        return [[(x - self.offset) / self.scale] for x in data]

    def invert(self):
        return Descaling(parameters=self._parameters)


class Descaling(Scaling):

    def __init__(self, offset=None, scale=None, parameters=None):
        super(Descaling, self).__init__(offset=offset, scale=scale, parameters=parameters)

    def apply(self, data):
        return [[(x * self.scale + self.offset)] for x in data]

    def invert(self):
        return Scaling(parameters=self._parameters)


def mean_stddev(data, corrected=False):
    n = float(len(data))
    mean = sum(data) / n
    var = sum(math.pow(x - mean, 2) for x in data)
    if corrected:
        stddev = math.sqrt(var / (n - 1))
    else:
        stddev = math.sqrt(var / n)
    return mean, stddev
