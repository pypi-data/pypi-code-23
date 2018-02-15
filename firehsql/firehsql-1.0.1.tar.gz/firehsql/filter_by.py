import logging
from dateutil.parser import parse as dateparse

from .expressions import Expression
from .field import Field


class SQLFilter(object):

    sql = None
    fields = None
    separator = ' AND '

    def __init__(self, sql):
        self.sql = sql
        self.fields = []


    def add(self, field_tuple):
        if field_tuple is None:
            pass

        elif isinstance(field_tuple, SQLFilter):
            self.fields.append(field_tuple)

        elif isinstance(field_tuple, (list, tuple)):
            if isinstance(field_tuple[0], Field):
                field = field_tuple[0]
            else:
                field = self.sql.field(field_tuple[0])
            self.sql.validate_filter_field_name(field)

            value = field_tuple[1]
            if isinstance(value, Field):
                self.sql.validate_filter_field_name(value)
            elif isinstance(value, Expression):
                value.validate_as_filter(self.sql)

            if len(field_tuple) > 2:
                operator = field_tuple[2]
            else:
                operator = '='

            self.fields.append((field, value, operator))

        else:
            raise TypeError('Expecting SQLFilter, list, or tuple.')


    @property
    def data(self):
        for field_tuple in self.fields:
            if isinstance(field_tuple, SQLFilter):
                for data in field_tuple.data:
                    yield data
            elif field_tuple[1] is None:
                pass
            elif isinstance(field_tuple[1], Field):
                pass
            elif isinstance(field_tuple[1], Expression):
                for data in field_tuple[1].data:
                    yield data
            elif isinstance(field_tuple[1], (list, tuple)):
                for data in field_tuple[1]:
                    yield data
            else:
                yield field_tuple[1]


    def __str__(self):
        filters = []
        # field_tuple: (field_name, value, operator) or SQLFilter
        for field_tuple in self.fields:
            if isinstance(field_tuple, SQLFilter):
                filter_expression = str(field_tuple)
                if filter_expression:
                    if len(field_tuple.fields) > 1:
                        filters.append('(%s)' % filter_expression)
                    else:
                        filters.append(filter_expression)
                continue

            expression = [str(field_tuple[0])]
            if len(field_tuple) == 3:
                expression.append(field_tuple[2])

            if field_tuple[1] is None:
                expression.append('NULL')

            elif isinstance(field_tuple[1], Field):
                expression.append(str(field_tuple[1]))

            elif isinstance(field_tuple[1], Expression):
                expression.append(str(field_tuple[1]))

            elif isinstance(field_tuple[1], (list, tuple)):
                if not field_tuple[1]:
                    continue

                expression.append('(%s)' % ', '.join(
                        [self.sql.schema.PLACEHOLDER] * len(field_tuple[1])))
            else:
                expression.append(self.sql.schema.PLACEHOLDER)

            filters.append(' '.join(expression))

        return self.separator.join(filters)


class AndSQLFilter(SQLFilter): pass # pylint:disable=multiple-statements
class OrSQLFilter(SQLFilter):

    separator = ' OR '


class FilterByMixin(object):

    filters = None

    def __init__(self):
        super(FilterByMixin, self).__init__()
        self.filters = []


    def create_and_filter(self, *fields):
        filter_ = AndSQLFilter(self)
        for field in fields:
            filter_.add(field)

        return filter_


    def create_or_filter(self, *fields):
        filter_ = OrSQLFilter(self)
        for field in fields:
            filter_.add(field)

        return filter_


    def set_filters(self, *filters):
        flts = []
        for filter_ in filters:
            if isinstance(filter_, SQLFilter):
                self.filters.append(filter_)
            else:
                flts.append(filter_)

        if flts:
            self.filters.append(self.create_and_filter(*flts))


    def parse_adv_filters(self, data, fields):
        if not data:
            return None

        if isinstance(fields, dict):
            field_map = fields

        elif isinstance(fields, (list, tuple)):
            field_map = {}
            for field in fields:
                if isinstance(field, (list, tuple)):
                    if len(field) == 3:
                        field_map[field[1]] = (field[0], field[2])
                    elif len(field) == 2:
                        field_map[field[0]] = (field[0], field[1])
                    else:
                        field_map[field[0]] = (field[0], 'str')
                else:
                    field_map[field] = (field, 'str')
        else:
            return None

        if isinstance(data, dict):
            return self._parse_adv_keyval(data, field_map)

        elif isinstance(data, (list, tuple)):
            if data[0] == 'OR':
                filter_ = self.create_or_filter()
                data.pop(0)
            else:
                filter_ = self.create_and_filter()
                if data[0] == 'AND':
                    data.pop(0)

            for item in data:
                if isinstance(item, dict):
                    filter_.add(self._parse_adv_keyval(item, field_map))

                elif isinstance(item, (list, tuple)):
                    filter_.add(self.parse_adv_filters(item, field_map))

            return filter_

        return None


    def _parse_adv_keyval(self, data, field_map):
        filter_ = self.create_and_filter()

        for key, value in data.items():
            if not key in field_map:
                continue

            db_field, type_ = field_map[key]

            if isinstance(value, (list, tuple)):
                if value[0] == '!':
                    operator = 'NOT IN'
                    value.pop(0)
                else:
                    operator = 'IN'
                    if value[0] == '=':
                        value.pop(0)

                value = [self._parse_adv_value(v, type_) for v in value]
                filter_.add((db_field, value, operator))
                continue

            if value is None or len(value) < 2:
                continue

            if value[0] == '=':
                value = value[1:]
                if value == 'null':
                    filter_.add((db_field, None, 'IS'))
                else:
                    value = self._parse_adv_value(value, type_)
                    filter_.add((db_field, value, '='))

            elif value[0] == '!':
                value = value[1:]
                if value == 'null':
                    filter_.add((db_field, None, 'IS NOT'))
                else:
                    value = self._parse_adv_value(value, type_)
                    filter_.add((db_field, value, '<>'))

            elif (value[0] == '<' or value[0] == '>')  and value[1] == '=':
                operator = value[:2]
                value = self._parse_adv_value(value[2:], type_)
                filter_.add((db_field, value, operator))

            elif value[0] == '<' or value[0] == '>':
                operator = value[0]
                value = self._parse_adv_value(value[1:], type_)
                filter_.add((db_field, value, operator))

            elif value[0] == '%' or value[-1] == '%':
                value = self._parse_adv_value(value, 'str')
                filter_.add((db_field, value, 'LIKE'))

        return filter_


    def _parse_adv_value(self, value, type_):
        try:
            if value is None:
                return None
            elif type_ == 'str':
                return str(value)
            elif type_ == 'int':
                return int(value)
            elif type_ == 'date':
                return dateparse(value)

            return value
        except (TypeError, ValueError, OverflowError):
            logging.exception('Invalid Schema filter.')


    def find_filters(self, data, fields):
        if not data:
            return

        for field in fields:
            if isinstance(field, (list, tuple)):
                db_field = field[0]
                form_field = field[1]
            else:
                db_field = form_field = field

            value = data.get(form_field)
            if value is None or len(value) < 2:
                continue

            if value[0] == '=':
                value = value[1:]
                if value == 'null':
                    yield (db_field, None, 'IS')
                else:
                    yield (db_field, value, '=')

            elif value[0] == '!':
                value = value[1:]
                if value == 'null':
                    yield (db_field, None, 'IS NOT')
                else:
                    yield (db_field, value, '<>')

            elif (value[0] == '<' or value[0] == '>')  and value[1] == '=':
                yield (db_field, value[2:], value[:2])

            elif value[0] == '<' or value[0] == '>':
                yield (db_field, value[1:], value[0])

            elif value[0] == '%' or value[-1] == '%':
                yield (db_field, value, 'LIKE')


    def find_datetime_filters(self, data, *fields):
        for filter_ in self.find_filters(data, fields):
            if filter_[1] is None:
                yield filter_
                continue

            try:
                value = dateparse(filter_[1])
                yield (filter_[0], value, filter_[2])
            except (ValueError, OverflowError):
                logging.exception('Invalid Schema filter.')


    def find_numeric_filters(self, data, *fields):
        for filter_ in self.find_filters(data, fields):
            if filter_[1] is None:
                yield filter_
                continue

            try:
                value = int(filter_[1])
                yield (filter_[0], value, filter_[2])
            except (TypeError, ValueError):
                logging.exception('Invalid Schema filter.')
