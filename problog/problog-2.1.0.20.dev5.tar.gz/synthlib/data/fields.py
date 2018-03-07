from ..utils import AbstractMethod
from .transform import OneHotEncoding, LabelEncoding, ColumnTransformation, DummyColumnTransformation


class FieldType(object):

    def __init__(self):
        pass

    def to_numeric(self, categorical=False):
        """Transform this field into numerical data.

        :param categorical: allow multi-valued (otherwise use one-hot encoding)
        :type categorical: bool
        :return: transformation to apply
        :rtype: ColumnTransformation
        """
        raise AbstractMethod()


class CategoricalField(FieldType):

    def __init__(self, data=None, values=None, is_ordinal=False):
        super(CategoricalField, self).__init__()
        self._values = None
        if values is not None:
            self._values = values
        elif data is not None:
            self._values = list(set(data))
        else:
            raise ValueError('Creating a categorical field requires data or values.')
        self._is_ordinal = is_ordinal

    @property
    def values(self):
        """Give the possible values for this attribute.

        :return: list of possible values
        """
        return self._values

    @property
    def is_ordinal(self):
        """Is the field ordinal, that is, is there an order relation between the values?

        For example:
            red, green, blue -> No
            low, medium, high -> Yes

        :return: True if there is an order relation between the values, False otherwise
        """
        return self._is_ordinal

    def to_numeric(self, categorical=False):
        if categorical or self.is_ordinal:
            return LabelEncoding({x: i for i, x in enumerate(self.values)})
        else:
            return OneHotEncoding(self.values)

    def __repr__(self):
        values = ', '.join(self.values)
        if self.is_ordinal:
            return '[%s]' % values
        else:
            return '{%s}' % values


class NumericalField(FieldType):

    def __init__(self):
        super(NumericalField, self).__init__()

    def to_numeric(self, categorical=False):
        # no transformation required
        return DummyColumnTransformation()


class StringField(FieldType):

    def __init__(self):
        super(StringField, self).__init__()


class DateTimeField(FieldType):

    def __init__(self, format=None):
        super(DateTimeField, self).__init__()
        self._format = format
