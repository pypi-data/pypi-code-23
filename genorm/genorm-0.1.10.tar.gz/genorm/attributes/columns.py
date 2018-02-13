import datetime
import calendar
from pc23 import strlen
from .base import ColumnAttributeAbstract, OrmComparator
from ..values import AttributeValueInteger, AttributeValueFloat, AttributeValueString, AttributeValueBoolean, \
    AttributeValueBinary, AttributeValueDate, AttributeValueTime, AttributeValueDateTime, AttributeValueNull
from ..manage import manager
from ..utils import format_datetime, gettext
from ..exceptions import OrmValueVerificationError, OrmDefinitionError, OrmComparatorValueError


class ColumnIntegerAbstract(ColumnAttributeAbstract):
    def __init__(self, length, **kwargs):
        self.length = length
        self.big = kwargs.pop('big', False)
        self.unsigned = kwargs.pop('unsigned', False)
        self.require_nonzero = kwargs.pop('require_nonzero', False)
        if self.require_nonzero:
            kwargs['required'] = True
        super(ColumnIntegerAbstract, self).__init__(**kwargs)
        self.data_type = 'int'
        self.value_class = AttributeValueInteger
        if not self.nullable and not self._default and not self.auto_increment:
            self.default = 0
        self.override_null = 0
        self.strict_find = self.strict_find if self.strict_find is not None else True
        if self.is_version_key:
            self.nullable = bool(self.is_softdelete_key)
            self._default = 1
            self.unsigned = True

    def is_eq_with_tbl_schema(self, struct, session):
        if session.dbms_type == 'mysql':
            if (not self.big and str(struct['data_type']).lower() != 'int') \
                    or (self.big and str(struct['data_type']).lower() != 'bigint'):
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if not callable(self._default):
                if self._default is None and struct['column_default'] is not None:
                    return False
                elif self._default is not None and struct['column_default'] is None:
                    return False
                elif self._default is not None and int(self._default) != int(struct['column_default']):
                    return False
            elif struct['column_default'] is not None:
                return False
            if self.auto_increment and 'auto_increment' not in str(struct['extra']).lower():
                return False
            if self.unsigned and 'unsigned' not in str(struct['column_type']).lower():
                return False
        elif session.dbms_type == 'postgresql':
            if (not self.big and str(struct['data_type']).lower() != 'integer') \
                    or (self.big and str(struct['data_type']).lower() != 'bigint'):
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if self.auto_increment:
                nextval = "nextval('%s_%s_seq'::regclass)" % (self.model.table, self.tbl_k)
                if struct['column_default'] != nextval:
                    return False
            elif not callable(self._default):
                if self._default is None and struct['column_default'] is not None:
                    return False
                elif self._default is not None and struct['column_default'] is None:
                    return False
                elif self._default is not None and int(self._default) != int(struct['column_default']):
                    return False
            elif struct['column_default'] is not None:
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        if session.dbms_type == 'postgresql':
            data_type = ("BIGSERIAL" if self.big else "SERIAL") \
                if self.auto_increment \
                else ("BIGINT" if self.big else "INT")
        else:
            data_type = "BIGINT" if self.big else "INT"
        d.append(data_type)
        if self.unsigned and session.dbms_type == 'mysql':
            d.append('UNSIGNED')
        if not self.nullable and not self.auto_increment:
            d.append('NOT NULL')
        if self.auto_increment:
            if session.dbms_type == 'mysql':
                d.append('AUTO_INCREMENT')
        elif not callable(self._default) and self._default is not None:
            d.append('DEFAULT %i' % int(self._default))
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            data_type = ("BIGSERIAL" if self.big else "SERIAL") \
                if self.auto_increment \
                else ("BIGINT" if self.big else "INT")
            d.append("SET DATA TYPE %s" % data_type)
            d.append("DROP NOT NULL" if self.nullable else "SET NOT NULL")
            if not callable(self.default) and self.default is not None and not self.auto_increment:
                d.append("SET DEFAULT %i" % self._default)
            else:
                d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)

    def verify(self, value):
        value = super(ColumnIntegerAbstract, self).verify(value)
        if value is None:
            return None
        if '-' in str(value) and (str(value).index('-') != 0 or str(value).count('-') > 1):
            raise OrmValueVerificationError(gettext("Must be a number"))
        if not str(value).replace('-', '').isdigit():
            raise OrmValueVerificationError(gettext("Must be a number"))
        if self.unsigned and int(value) < 0:
            raise OrmValueVerificationError(gettext("Must be a positive number"))
        if self.require_nonzero and value == 0:
            raise OrmValueVerificationError(gettext("Is required"))
        return int(value)

    @property
    def empty_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', '0'))

    @property
    def notempty_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', '0'))

    @property
    def true_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', '0'))

    @property
    def false_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', '0'))


class ColumnFloatAbstract(ColumnAttributeAbstract):
    def __init__(self, length, decimals, **kwargs):
        if decimals is None and length is not None:
            raise OrmDefinitionError(
                "floating-point attribute types cannot be defined with 'length', but without 'decimal'!")
        elif decimals is not None and length is None:
            raise OrmDefinitionError(
                "floating-point attribute types cannot be defined with 'decimal', but without 'length'!")
        self.length = length
        self.decimals = decimals
        self.unsigned = bool(kwargs.pop('unsigned', False))
        self.big = kwargs.pop('big', False)
        self.require_nonzero = bool(kwargs.pop('require_nonzero', False))
        if self.require_nonzero:
            kwargs['required'] = True
        super(ColumnFloatAbstract, self).__init__(**kwargs)
        self.data_type = 'float'
        self.value_class = AttributeValueFloat
        if not self.nullable and not self._default:
            self._default = 0.0
        self.override_null = 0.0
        self.strict_find = self.strict_find if self.strict_find is not None else True

    def is_eq_with_tbl_schema(self, struct, session):
        if session.dbms_type == 'mysql':
            if (not self.big and str(struct['data_type']).lower() != 'float') \
                    or (self.big and str(struct['data_type']).lower() != 'double'):
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if not callable(self._default):
                if self._default is None and struct['column_default'] is not None:
                    return False
                elif self._default is not None and struct['column_default'] is None:
                    return False
                elif self._default is not None and float(self._default) != float(struct['column_default']):
                    return False
            elif struct['column_default'] is not None:
                return False
            if self.unsigned and 'unsigned' not in str(struct['column_type']).lower():
                return False
        elif session.dbms_type == 'postgresql':
            if (not self.big and str(struct['data_type']).lower() != 'real') \
                    or (self.big and str(struct['data_type']).lower() != 'double precision'):
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if not callable(self._default):
                if self._default is None and struct['column_default'] is not None:
                    return False
                elif self._default is not None and struct['column_default'] is None:
                    return False
                elif self._default is not None and float(self._default) != float(struct['column_default']):
                    return False
            elif struct['column_default'] is not None:
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        if session.dbms_type == 'postgresql':
            data_type = "DOUBLE PRECISION" if self.big else "REAL"
        elif session.dbms_type == 'mysql':
            data_type = "DOUBLE" if self.big else "FLOAT"
            if self.length and self.decimals:
                data_type += "(%i,%i)" % (int(self.length), int(self.decimals))
        else:
            raise TypeError("this column type is not supported for this database and has no alternative!")
        d.append(data_type)
        if self.unsigned and session.dbms_type == 'mysql':
            d.append('UNSIGNED')
        if not self.nullable:
            d.append('NOT NULL')
        if not callable(self._default) and self._default is not None:
            d.append('DEFAULT %f' % float(self._default))
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            data_type = "DOUBLE PRECISION" if self.big else "REAL"
            d.append("SET DATA TYPE %s" % data_type)
            d.append("DROP NOT NULL" if self.nullable else "SET NOT NULL")
            if not callable(self.default) and self.default is not None:
                d.append("SET DEFAULT %f" % float(self._default))
            else:
                d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)

    def verify(self, value):
        value = super(ColumnFloatAbstract, self).verify(value)
        if value is None:
            return None
        if '-' in str(value) and (str(value).index('-') != 0 or str(value).count('-') > 1):
            raise OrmValueVerificationError(gettext("Must be a floating-point number"))
        if str(value).count('.') > 1:
            raise OrmValueVerificationError(gettext("Must be a floating-point number"))
        if not str(value).replace('-', '').replace('.', '').isdigit():
            raise OrmValueVerificationError(gettext("Must be a floating-point number"))
        if self.unsigned and float(value) < 0:
            raise OrmValueVerificationError(gettext("Must be a positive floating-point number"))
        if self.require_nonzero and value == 0:
            raise OrmValueVerificationError(gettext("Is required"))
        return float(value)

    @property
    def empty_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', '0'))

    @property
    def notempty_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', '0'))

    @property
    def true_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', '0'))

    @property
    def false_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', '0'))


class ColumnNumericAbstract(ColumnAttributeAbstract):
    def __init__(self, precision, scale, **kwargs):
        if not precision or not scale:
            raise OrmDefinitionError("numeric attribute types cannot be defined without 'precision' or 'scale'!")
        self.precision = int(precision)
        self.scale = int(scale)
        self.unsigned = bool(kwargs.pop('unsigned', False))
        self.require_nonzero = bool(kwargs.pop('require_nonzero', False))
        if self.require_nonzero:
            kwargs['required'] = True
        super(ColumnNumericAbstract, self).__init__(**kwargs)
        self.data_type = 'float'
        self.value_class = AttributeValueFloat
        if not self.nullable and not self._default:
            self._default = 0.0
        self.override_null = 0.0
        self.strict_find = self.strict_find if self.strict_find is not None else True

    def is_eq_with_tbl_schema(self, struct, session):
        if session.dbms_type == 'mysql':
            if str(struct['data_type']).lower() not in ('numeric', 'decimal'):
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if not callable(self._default):
                if self._default is None and struct['column_default'] is not None:
                    return False
                elif self._default is not None and struct['column_default'] is None:
                    return False
                elif self._default is not None and float(self._default) != float(struct['column_default']):
                    return False
            elif struct['column_default'] is not None:
                return False
            if self.unsigned and 'unsigned' not in str(struct['column_type']).lower():
                return False
            if int(self.precision) != int(struct['numeric_precision']):
                return False
            if int(self.scale) != int(struct['numeric_scale']):
                return False
        elif session.dbms_type == 'postgresql':
            if str(struct['data_type']).lower() != 'numeric':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if not callable(self._default):
                if self._default is None and struct['column_default'] is not None:
                    return False
                elif self._default is not None and struct['column_default'] is None:
                    return False
                elif self._default is not None and float(self._default) != float(struct['column_default']):
                    return False
            elif struct['column_default'] is not None:
                return False
            if int(self.precision) != int(struct['numeric_precision']):
                return False
            if int(self.scale) != int(struct['numeric_scale']):
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        if session.dbms_type == 'postgresql':
            data_type = "NUMERIC(%i,%i)" % (self.precision, self.scale)
        elif session.dbms_type == 'mysql':
            data_type = "DECIMAL(%i,%i)" % (self.precision, self.scale)
        else:
            raise TypeError("this column type is not supported for this database and has no alternative!")
        d.append(data_type)
        if self.unsigned and session.dbms_type == 'mysql':
            d.append('UNSIGNED')
        if not self.nullable:
            d.append('NOT NULL')
        if not callable(self._default) and self._default is not None:
            d.append('DEFAULT %f' % float(self._default))
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            data_type = "NUMERIC(%i,%i)" % (self.precision, self.scale)
            d.append("SET DATA TYPE %s" % data_type)
            d.append("DROP NOT NULL" if self.nullable else "SET NOT NULL")
            if not callable(self.default) and self.default is not None:
                d.append("SET DEFAULT %f" % float(self._default))
            else:
                d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)

    @property
    def empty_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', '0'))

    @property
    def notempty_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', '0'))

    @property
    def true_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', '0'))

    @property
    def false_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', '0'))


class ColumnDatetimeAbstract(ColumnAttributeAbstract):
    def __init__(self, fsp=None, **kwargs):
        self.fsp = fsp
        self.with_time_zone = bool(kwargs.pop('with_time_zone', True))
        super(ColumnDatetimeAbstract, self).__init__(**kwargs)
        self.data_type = 'datetime'
        self.value_class = AttributeValueDateTime
        self.strict_find = self.strict_find if self.strict_find is not None else True
        self.full_format = bool(kwargs.pop('full_format', False))
        self.format = kwargs.pop('format', None)
        self.use24hours = bool(kwargs.pop('use24hours', None))

    def represent_for_write(self, value, session):
        if self.with_time_zone and session.dbms_type == 'mysql' \
                and (value is None or isinstance(value, AttributeValueNull)):
            return '0000-00-00 00:00:00'
        return value

    def is_eq_with_tbl_schema(self, struct, session):
        if session.dbms_type == 'mysql':
            if str(struct['data_type']).lower() != ('timestamp' if self.with_time_zone else 'datetime'):
                return False
            if not self.with_time_zone and bool(struct['is_nullable']) != bool(self.nullable):
                return False
            if int(struct['datetime_precision']) != (int(self.fsp) if self.fsp is not None else 0):
                return False
            if self.with_time_zone \
                    and (struct['column_default'][:19] != '0000-00-00 00:00:00' or struct['extra']):
                return False
        elif session.dbms_type == 'postgresql':
            if str(struct['data_type']).lower() != ('timestamp with time zone'
                                                    if self.with_time_zone
                                                    else 'timestamp without time zone'):
                return False
            if bool(self.nullable) != bool(struct['is_nullable']):
                return False
            if int(struct['datetime_precision']) != (int(self.fsp) if self.fsp is not None else 6):
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        if session.dbms_type == 'postgresql':
            if self.with_time_zone:
                data_type = "TIMESTAMP WITH TIME ZONE" \
                    if not self.fsp \
                    else "TIMESTAMP(%i) WITH TIME ZONE" % int(self.fsp)
            else:
                data_type = "TIMESTAMP WITHOUT TIME ZONE" \
                    if not self.fsp \
                    else "TIMESTAMP(%i) WITHOUT TIME ZONE" % int(self.fsp)
        elif session.dbms_type == 'mysql':
            if self.with_time_zone:
                data_type = "TIMESTAMP" if not self.fsp else "TIMESTAMP(%i)" % int(self.fsp)
            else:
                data_type = "DATETIME" if not self.fsp else "DATETIME(%i)" % int(self.fsp)
        else:
            raise TypeError("this column type is not supported for this database and has no alternative!")
        d.append(data_type)
        if not self.nullable and (session.dbms_type != 'mysql' or not self.with_time_zone):
            d.append('NOT NULL')
        if session.dbms_type == 'mysql' and self.with_time_zone:
            d.append("DEFAULT 0")
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            if self.with_time_zone:
                data_type = "TIMESTAMP WITH TIME ZONE" \
                    if not self.fsp \
                    else "TIMESTAMP(%i) WITH TIME ZONE" % int(self.fsp)
            else:
                data_type = "TIMESTAMP WITHOUT TIME ZONE" \
                    if not self.fsp \
                    else "TIMESTAMP(%i) WITHOUT TIME ZONE" % int(self.fsp)
            d.append("SET DATA TYPE %s" % data_type)
            d.append("DROP NOT NULL" if self.nullable else "SET NOT NULL")
            d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)

    def text_repr(self, value, instance=None):
        if value is None:
            return ""
        session = manager.get_session(instance=instance)
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            format_ = self.format or \
                      (manager.get_full_date_format(session=session)
                       if self.full_format
                       else manager.get_short_date_format(session=session))
        elif isinstance(value, datetime.time):
            format_ = self.format or \
                      (manager.get_full_time_format(session=session)
                       if self.full_format
                       else manager.get_short_time_format(session=session))
        else:
            dateformat_ = self.format or \
                          (manager.get_full_date_format(session=session)
                           if self.full_format
                           else manager.get_short_date_format(session=session))
            timeformat_ = self.format or \
                          (manager.get_full_time_format(session=session)
                           if self.full_format
                           else manager.get_short_time_format(session=session))
            format_ = dateformat_ + " " + timeformat_
        return format_datetime(value, format_)

    @staticmethod
    def _verify_fail():
        raise OrmValueVerificationError(gettext("Must be a valid date and time"))

    def verify(self, value):
        value = super(ColumnDatetimeAbstract, self).verify(value)
        if value is None:
            return None
        if isinstance(value, str):
            ps = value.split(' ')
            d_ = False
            t_ = False
            n_year = 0
            n_month = 0
            n_day = 0
            n_hour = 0
            n_minute = 0
            n_second = 0
            for p in ps:
                if not p:
                    continue
                if '.' not in p and '/' not in p and '\\' not in p and '-' not in p and ':' not in p:
                    self._verify_fail()
                if ':' in p:
                    if t_:
                        self._verify_fail()
                    if p.count(':') > 2:
                        self._verify_fail()
                    p_ = p.split(':')
                    if not p_[0].isdigit() or not p_[1].isdigit() or (len(p_) == 3 and not p_[2].isdigit()):
                        self._verify_fail()
                    n_hour = int(p_[0])
                    n_minute = int(p_[1])
                    n_second = int(p_[2]) if len(p) == 3 else 0
                    if n_hour > 23 or n_minute > 59 or n_second > 59:
                        self._verify_fail()
                    t_ = True
                else:
                    if d_:
                        self._verify_fail()
                    s = '.' if '.' in p else ('-' if '-' in p else ('/' if '/' in p else '\\'))
                    p_ = p.split(s)
                    if len(p_) != 3:
                        self._verify_fail()
                    if not p_[0].isdigit() or not p_[1].isdigit() or not p_[2].isdigit():
                        self._verify_fail()
                    p1 = int(p_[0])
                    p2 = int(p_[1])
                    p3 = int(p_[2])
                    starting_with_year = p1 > 31 or s == '-'
                    if starting_with_year:
                        n_year = p1
                        if s in ('.', '-'):
                            n_month = p2
                            n_day = p3
                        else:
                            n_month = p3
                            n_day = p2
                    else:
                        n_year = p3
                        if s in ('.', '-'):
                            n_month = p2
                            n_day = p1
                        else:
                            n_month = p1
                            n_day = p2
                    if 99 < n_year < 1000:
                        self._verify_fail()
                    if n_year < 1000:
                        n_year = n_year + 1000 if n_year > 69 else n_year + 2000
                    if n_day == 0 or n_month == 0 or n_day > 31 or n_month > 12:
                        self._verify_fail()
                    n_daysmax = calendar.monthrange(n_year, n_month)[1]
                    if n_day > n_daysmax:
                        self._verify_fail()
                    d_ = True
            if not d_ or not t_:
                self._verify_fail()
            value = datetime.datetime(n_year, n_month, n_day, n_hour, n_minute, n_second)
        elif not isinstance(value, datetime.datetime):
            self._verify_fail()
        return value

    @property
    def empty_(self):
        return OrmComparator(self, 'FALSE')

    @property
    def notempty_(self):
        return OrmComparator(self, 'TRUE')

    @property
    def true_(self):
        return OrmComparator(self, 'TRUE')

    @property
    def false_(self):
        return OrmComparator(self, 'FALSE')

    def resolve_comparator_(self, cmp, session):
        from ..funcs import or_, and_
        if cmp.cmp == 'TRUE':
            if session.dbms_type == 'mysql':
                return and_(OrmComparator(cmp.item, '!=', '0000-00-00 00:00:00'), OrmComparator(cmp.item, '!ISNULL'))
            elif session.dbms_type == 'postgresql':
                return OrmComparator(cmp.item, '!ISNULL')
        elif cmp.cmp == 'FALSE':
            if session.dbms_type == 'mysql':
                return or_(OrmComparator(cmp.item, '=', '0000-00-00 00:00:00'), OrmComparator(cmp.item, 'ISNULL'))
            elif session.dbms_type == 'postgresql':
                return OrmComparator(cmp.item, 'ISNULL')
        return cmp


class ColumnDateAbstract(ColumnAttributeAbstract):
    def __init__(self, **kwargs):
        super(ColumnDateAbstract, self).__init__(**kwargs)
        self.data_type = 'date'
        self.value_class = AttributeValueDate
        self.strict_find = self.strict_find if self.strict_find is not None else True
        self.full_format = bool(kwargs.pop('full_format', False))
        self.format = kwargs.pop('format', None)

    def is_eq_with_tbl_schema(self, struct, session):
        if session in ('mysql', 'postgresql'):
            if str(struct['data_type']).lower() != 'date':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        d.append("DATE")
        if not self.nullable:
            d.append('NOT NULL')
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            d.append("SET DATA TYPE DATE")
            d.append("DROP NOT NULL" if self.nullable else "SET NOT NULL")
            d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)

    def text_repr(self, value, instance=None):
        if value is None:
            return ""
        session = manager.get_session(instance=instance)
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            format_ = self.format or \
                      (manager.get_full_date_format(session=session)
                       if self.full_format
                       else manager.get_short_date_format(session=session))
        elif isinstance(value, datetime.time):
            format_ = self.format or \
                      (manager.get_full_time_format(session=session)
                       if self.full_format
                       else manager.get_short_time_format(session=session))
        else:
            dateformat_ = self.format or \
                          (manager.get_full_date_format(session=session)
                           if self.full_format
                           else manager.get_short_date_format(session=session))
            timeformat_ = self.format or \
                          (manager.get_full_time_format(session=session)
                           if self.full_format
                           else manager.get_short_time_format(session=session))
            format_ = dateformat_ + " " + timeformat_
        return format_datetime(value, format_)

    @staticmethod
    def _verify_fail():
        raise OrmValueVerificationError(gettext("Must be a valid date"))

    def verify(self, value):
        value = super(ColumnDateAbstract, self).verify(value)
        if value is None:
            return None
        if isinstance(value, str):
            ps = value.split(' ')
            d_ = False
            n_year = 0
            n_month = 0
            n_day = 0
            for p in ps:
                if not p:
                    continue
                if '.' not in p and '/' not in p and '\\' not in p and '-' not in p and ':' not in p:
                    self._verify_fail()
                if ':' in p:
                    self._verify_fail()
                else:
                    if d_:
                        self._verify_fail()
                    s = '.' if '.' in p else ('-' if '-' in p else ('/' if '/' in p else '\\'))
                    p_ = p.split(s)
                    if len(p_) != 3:
                        self._verify_fail()
                    if not p_[0].isdigit() or not p_[1].isdigit() or not p_[2].isdigit():
                        self._verify_fail()
                    p1 = int(p_[0])
                    p2 = int(p_[1])
                    p3 = int(p_[2])
                    starting_with_year = p1 > 31 or s == '-'
                    if starting_with_year:
                        n_year = p1
                        if s in ('.', '-'):
                            n_month = p2
                            n_day = p3
                        else:
                            n_month = p3
                            n_day = p2
                    else:
                        n_year = p3
                        if s in ('.', '-'):
                            n_month = p2
                            n_day = p1
                        else:
                            n_month = p1
                            n_day = p2
                    if 99 < n_year < 1000:
                        self._verify_fail()
                    if n_year < 1000:
                        n_year = n_year + 1000 if n_year > 69 else n_year + 2000
                    if n_day == 0 or n_month == 0 or n_day > 31 or n_month > 12:
                        self._verify_fail()
                    n_daysmax = calendar.monthrange(n_year, n_month)[1]
                    if n_day > n_daysmax:
                        self._verify_fail()
                    d_ = True
            if not d_:
                self._verify_fail()
            value = datetime.date(n_year, n_month, n_day)
        elif not isinstance(value, datetime.date):
            self._verify_fail()
        return value

    @property
    def empty_(self):
        return OrmComparator(self, 'FALSE')

    @property
    def notempty_(self):
        return OrmComparator(self, 'TRUE')

    @property
    def true_(self):
        return OrmComparator(self, 'TRUE')

    @property
    def false_(self):
        return OrmComparator(self, 'FALSE')

    def resolve_comparator_(self, cmp, session):
        from ..funcs import or_, and_
        if cmp.cmp == 'TRUE':
            if session.dbms_type == 'mysql':
                return and_(OrmComparator(cmp.item, '!=', '0000-00-00'), OrmComparator(cmp.item, '!ISNULL'))
            elif session.dbms_type == 'postgresql':
                return OrmComparator(cmp.item, '!ISNULL')
        elif cmp.cmp == 'FALSE':
            if session.dbms_type == 'mysql':
                return or_(OrmComparator(cmp.item, '=', '0000-00-00'), OrmComparator(cmp.item, 'ISNULL'))
            elif session.dbms_type == 'postgresql':
                return OrmComparator(cmp.item, 'ISNULL')
        return cmp


class ColumnTimeAbstract(ColumnAttributeAbstract):
    def __init__(self, fsp=None, **kwargs):
        self.fsp = fsp
        super(ColumnTimeAbstract, self).__init__(**kwargs)
        self.data_type = 'time'
        self.value_class = AttributeValueTime
        self.strict_find = self.strict_find if self.strict_find is not None else True
        self.full_format = bool(kwargs.pop('full_format', False))
        self.format = kwargs.pop('format', None)
        self.use24hours = bool(kwargs.pop('use24hours', None))

    def is_eq_with_tbl_schema(self, struct, session):
        if session.dbms_type == 'mysql':
            if str(struct['data_type']).lower() != 'time':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if int(struct['datetime_precision']) != (int(self.fsp) if self.fsp is not None else 0):
                return False
        elif session.dbms_type == 'postgresql':
            if str(struct['column_type']).lower() != 'time':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if int(struct['datetime_precision']) != (int(self.fsp) if self.fsp is not None else 6):
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        d.append("TIME" if not self.fsp else "TIME(%i)" % int(self.fsp))
        if not self.nullable:
            d.append('NOT NULL')
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            d.append("SET DATA TYPE TIME")
            d.append("DROP NOT NULL" if self.nullable else "SET NOT NULL")
            d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)

    def text_repr(self, value, instance=None):
        if value is None:
            return ""
        session = manager.get_session(instance=instance)
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            format_ = self.format or \
                      (manager.get_full_date_format(session=session)
                       if self.full_format
                       else manager.get_short_date_format(session=session))
        elif isinstance(value, datetime.time):
            format_ = self.format or \
                      (manager.get_full_time_format(session=session)
                       if self.full_format
                       else manager.get_short_time_format(session=session))
        else:
            dateformat_ = self.format or \
                          (manager.get_full_date_format(session=session)
                           if self.full_format
                           else manager.get_short_date_format(session=session))
            timeformat_ = self.format or \
                          (manager.get_full_time_format(session=session)
                           if self.full_format
                           else manager.get_short_time_format(session=session))
            format_ = dateformat_ + " " + timeformat_
        return format_datetime(value, format_)

    @staticmethod
    def _verify_fail():
        raise OrmValueVerificationError(gettext("Must be a valid time"))

    def verify(self, value):
        value = super(ColumnTimeAbstract, self).verify(value)
        if value is None:
            return None
        if isinstance(value, str):
            ps = value.split(' ')
            t_ = False
            n_hour = 0
            n_minute = 0
            n_second = 0
            for p in ps:
                if not p:
                    continue
                if '.' not in p and '/' not in p and '\\' not in p and '-' not in p and ':' not in p:
                    self._verify_fail()
                if ':' in p:
                    if t_:
                        self._verify_fail()
                    if p.count(':') > 2:
                        self._verify_fail()
                    p_ = p.split(':')
                    if not p_[0].isdigit() or not p_[1].isdigit() or (len(p_) == 3 and not p_[2].isdigit()):
                        self._verify_fail()
                    n_hour = int(p_[0])
                    n_minute = int(p_[1])
                    n_second = int(p_[2]) if len(p) == 3 else 0
                    if n_hour > 23 or n_minute > 59 or n_second > 59:
                        self._verify_fail()
                    t_ = True
                else:
                    self._verify_fail()
            if not t_:
                self._verify_fail()
            value = datetime.time(n_hour, n_minute, n_second)
        elif not isinstance(value, datetime.time):
            self._verify_fail()
        return value

    @property
    def empty_(self):
        return OrmComparator(self, 'FALSE')

    @property
    def notempty_(self):
        return OrmComparator(self, 'TRUE')

    @property
    def true_(self):
        return OrmComparator(self, 'TRUE')

    @property
    def false_(self):
        return OrmComparator(self, 'FALSE')

    def resolve_comparator_(self, cmp, session):
        if cmp.cmp == 'TRUE':
            return OrmComparator(cmp.item, '!ISNULL')
        elif cmp.cmp == 'FALSE':
            return OrmComparator(cmp.item, 'ISNULL')
        return cmp


class ColumnStringAbstract(ColumnAttributeAbstract):
    def __init__(self, length=255, **kwargs):
        if length > 65535:
            raise OrmDefinitionError("string attribute types cannot be longer than 65535 symbols length!")
        elif length < 1:
            raise OrmDefinitionError("string attribute types' must be at least one symbol length!")
        self.length = length
        self.collate_ci = kwargs.pop('collate_ci', False)
        self.max_chars = kwargs.pop('max_chars', None)
        if self.max_chars is not None and not isinstance(self.max_chars, int):
            raise TypeError("'max_chars' must be None or (int) type!")
        super(ColumnStringAbstract, self).__init__(**kwargs)
        self.data_type = 'str'
        self.value_class = AttributeValueString
        if not self.nullable and not self._default:
            self._default = ''
        self.override_null = ''
        self.strict_find = self.strict_find if self.strict_find is not None else False

    def is_eq_with_tbl_schema(self, struct, session):
        if session.dbms_type == 'mysql':
            if str(struct['data_type']).lower() != 'varchar':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if struct['character_maximum_length'] != self.length:
                return False
            if not callable(self._default):
                if self._default is None and struct['column_default'] is not None:
                    return False
                elif self._default is not None and struct['column_default'] is None:
                    return False
                elif self._default is not None and str(self._default) != str(struct['column_default']):
                    return False
            elif struct['column_default'] is not None:
                return False
        elif session.dbms_type == 'postgresql':
            if str(struct['column_type']).lower() != 'varchar':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            pg_attr_default = None \
                if self.default is None \
                else "'%s'::character varying" % str(self.default)
            if not callable(self._default):
                if self._default is None and struct['column_default'] is not None:
                    return False
                elif self._default is not None and struct['column_default'] is None:
                    return False
                elif self._default is not None and pg_attr_default != str(struct['column_default']):
                    return False
            elif struct['column_default'] is not None:
                return False
            if struct['character_maximum_length'] != self.length:
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        d.append("VARCHAR(%i)" % self.length)
        if session.dbms_type == 'mysql':
            d.append("CHARACTER SET utf8 COLLATE utf8_bin")
        if not self.nullable:
            d.append('NOT NULL')
        if not callable(self._default) and self._default is not None:
            d.append("DEFAULT '%s'" % str(self._default).replace('\\', '\\\\').replace("'", "\'").replace("\n", "\\n"))
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            d.append("SET DATA TYPE VARCHAR(%i)" % self.length)
            d.append("DROP NOT NULL" if self.nullable else "SET NOT NULL")
            if not callable(self._default) and self._default is not None:
                d.append("SET DEFAULT '%s'"
                         % str(self._default).replace('\\', '\\\\').replace("'", "\'").replace("\n", "\\n"))
            else:
                d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)

    def verify(self, value):
        value = super(ColumnStringAbstract, self).verify(value)
        if value is None:
            return None
        if self.max_chars and strlen(value) > int(self.max_chars):
            raise OrmValueVerificationError(gettext("Must be not longer than %i characters" % self.max_chars))
        return str(value)

    @property
    def empty_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', ''))

    @property
    def notempty_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', ''))

    @property
    def true_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', ''))

    @property
    def false_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', ''))

    def contains_(self, value):
        return self.like_("%%%s%%" % value)

    def not_contains_(self, value):
        return self.notlike_("%%%s%%" % value)


class ColumnTextAbstract(ColumnAttributeAbstract):
    def __init__(self, **kwargs):
        self.max_chars = kwargs.pop('max_chars', None)
        if self.max_chars is not None and not isinstance(self.max_chars, int):
            raise TypeError("'max_chars' must be None or (int) type!")
        self.big = kwargs.pop('big', False)
        super(ColumnTextAbstract, self).__init__(**kwargs)
        self.data_type = 'text'
        self.value_class = AttributeValueString
        self.strict_find = self.strict_find if self.strict_find is not None else False

    def is_eq_with_tbl_schema(self, struct, session):
        if session.dbms_type == 'mysql':
            if str(struct['data_type']).lower() != ('longtext' if self.big else 'text'):
                return False
        elif session.dbms_type == 'postgresql':
            if str(struct['data_type']) != 'text':
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        if session.dbms_type == 'mysql':
            d.append("TEXT" if not self.big else "LONGTEXT")
        else:
            d.append("TEXT")
        if session.dbms_type == 'mysql':
            d.append("CHARACTER SET utf8 COLLATE utf8_bin")
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            d.append("SET DATA TYPE TEXG")
            d.append("DROP NOT NULL" if self.nullable else "SET NOT NULL")
            d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)

    def verify(self, value):
        value = super(ColumnTextAbstract, self).verify(value)
        if value is None:
            return None
        if self.max_chars and strlen(value) > int(self.max_chars):
            raise OrmValueVerificationError(gettext("Must be not longer than %i characters" % self.max_chars))
        return str(value)

    @property
    def empty_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', ''))

    @property
    def notempty_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', ''))

    @property
    def true_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', ''))

    @property
    def false_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', ''))

    def contains_(self, value):
        return self.like_("%%%s%%" % value)

    def not_contains_(self, value):
        return self.notlike_("%%%s%%" % value)


class ColumnBlobAbstract(ColumnAttributeAbstract):
    def __init__(self, **kwargs):
        self.big = kwargs.pop('big', False)
        super(ColumnBlobAbstract, self).__init__(**kwargs)
        self.data_type = 'blob'
        self.value_class = AttributeValueBinary
        self.strict_find = self.strict_find if self.strict_find is not None else False

    def is_eq_with_tbl_schema(self, struct, session):
        if session.dbms_type == 'mysql':
            if str(struct['data_type']).lower() != ('longblob' if self.big else 'blob'):
                return False
        elif session.dbms_type == 'postgresql':
            if str(struct['data_type']).lower() != 'bytea':
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        if session.dbms_type == 'mysql':
            d.append("BLOB" if not self.big else "LONGBLOB")
        else:
            d.append("BYTEA")
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            d.append("SET DATA TYPE BYTEA")
            d.append("DROP NOT NULL")
            d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)

    @property
    def empty_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', ''))

    @property
    def notempty_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', ''))

    @property
    def true_(self):
        from ..funcs import and_
        return and_(OrmComparator(self, '!ISNULL'), OrmComparator(self, '!=', ''))

    @property
    def false_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, '=', ''))


class ColumnBooleanAbstract(ColumnAttributeAbstract):
    def __init__(self, **kwargs):
        self.boolean = True
        if kwargs.get('is_softdelete_key', False):
            kwargs['nullable'] = kwargs.get('nullable', False)
            kwargs['default'] = kwargs.get('default', False)
        super(ColumnBooleanAbstract, self).__init__(**kwargs)
        self.override_null = False
        self.data_type = 'bool'
        self.value_class = AttributeValueBoolean

    def is_eq_with_tbl_schema(self, struct, session):
        if session.dbms_type == 'mysql':
            if str(struct['data_type']).lower() != 'tinyint':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if not callable(self._default):
                if self._default is None and struct['column_default'] is not None:
                    return False
                elif self._default is not None and struct['column_default'] is None:
                    return False
                elif self._default is not None and bool(self._default) != bool(struct['column_default']):
                    return False
            elif struct['column_default'] is not None:
                return False
        elif session.dbms_type == 'postgresql':
            if str(struct['data_type']).lower() != 'boolean':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            attr_default = None \
                if callable(self._default) \
                else (bool(self._default) if self._default is not None else None)
            column_default = None \
                if struct['column_default'] is None \
                else (True if str(struct['column_default']).lower() in ('true', 'y', 'yes') else False)
            if not callable(self._default):
                if attr_default is None and column_default is not None:
                    return False
                elif attr_default is not None and column_default is None:
                    return False
                elif attr_default is not None and attr_default != column_default:
                    return False
            elif struct['column_default'] is not None:
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        d.append("BOOL")
        if not self.nullable and not self.auto_increment:
            d.append('NOT NULL')
        if not callable(self._default) and self._default is not None:
            d.append('DEFAULT TRUE' if bool(self._default) else 'DEFAULT FALSE')
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            d.append("SET DATA TYPE BOOL")
            d.append("DROP NOT NULL" if self.nullable else "SET NOT NULL")
            if not callable(self._default) and self._default is not None:
                d.append("SET DEFAULT %s" % ("TRUE" if bool(self._default) else "FALSE"))
            else:
                d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)

    def like_(self, value):
        raise OrmComparatorValueError("boolean attribute types cannot be filtered using `like_` or `notlike_`!")

    def notlike_(self, value):
        raise OrmComparatorValueError("boolean attribute types cannot be filtered using `like_` or `notlike_`!")

    @property
    def empty_(self):
        from ..funcs import or_
        return or_(OrmComparator(self, 'ISNULL'), OrmComparator(self, 'FALSE'))

    @property
    def notempty_(self):
        return OrmComparator(self, 'TRUE')

