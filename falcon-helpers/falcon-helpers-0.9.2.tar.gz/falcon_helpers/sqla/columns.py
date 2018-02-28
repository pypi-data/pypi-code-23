import ast
import pathlib
import sqlalchemy as sa
import sqlalchemy.types as types


class CartesianPoint:
    def __init__(self, point):
        self._raw = point
        self.x = point[0]
        self.y = point[1]

    def __getitem__(self, key):
        return self._raw[key]

    def __str__(self):
        return self._raw


class Path(types.TypeDecorator):
    """Automatically coerces a pathlib.Path to Unicode and back again"""

    impl = types.Unicode

    def process_bind_param(self, value, dialect):

        if isinstance(value, (pathlib.PurePath, str)):
            return str(value)
        elif value is None:
            return None
        else:
            raise TypeError(f'Unable to store {type(value)}')

    def process_result_value(self, value, dialect):
        if value:
            return pathlib.Path(value)

    def copy(self, **kw):
        return Path(self.impl.length)


class Point(types.UserDefinedType):

    def get_col_spec(self):
        return 'point'

    def bind_processor(self, dialect):
        def process(value):
            # Just in case this is null, we should allow it, the DB will cath
            # nullability
            if value is None:
                return None

            return str(value)
        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if not value:
                return None

            v = ast.literal_eval(value)
            return CartesianPoint(v)
        return process
