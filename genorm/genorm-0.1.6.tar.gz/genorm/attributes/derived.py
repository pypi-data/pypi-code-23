import uuid
import re
import datetime
import hashlib
from .base import OrmComparator
from .columns import ColumnIntegerAbstract, ColumnFloatAbstract, ColumnNumericAbstract, ColumnDatetimeAbstract, \
    ColumnDateAbstract, ColumnTimeAbstract, ColumnStringAbstract, ColumnTextAbstract, ColumnBlobAbstract, \
    ColumnBooleanAbstract, ColumnAttributeAbstract
from ..values import AttributeValueNull, AttributeValueString, ValueYearMonth, ValuePhone, ValueIPRequesties, \
    ValueDimensions2D, ValueDimensions3D, ValuePoint, ValueBox, ValueVector, ValueGeoCoordinate, ValuePassword
from ..funcs import if_, uncastable_, inet6_aton_, inet6_ntoa_, host_, concat_ws_, substr_, concat_, unhex_, length_, \
    conv_, hex_, pg_text_
from ..utils import gettext, ipaddr_version, ipv4mask_2_cidr
from ..manage import manager
from ..exceptions import OrmValueVerificationError, OrmPasswordIsWeak, OrmProhibittedValueSet, OrmValueError, \
    OrmDefinitionError, OrmParameterError


PASSWORD_ALGORYTHM_PLAIN = 'plain'
PASSWORD_ALGORYTHM_MD5 = 'md5'
PASSWORD_ALGORYTHM_SHA1 = 'sha1'
PASSWORD_ALGORYTHM_SHA224 = 'sha224'
PASSWORD_ALGORYTHM_SHA256 = 'sha256'
PASSWORD_ALGORYTHM_SHA384 = 'sha384'
PASSWORD_ALGORYTHM_SHA512 = 'sha512'


class Integer(ColumnIntegerAbstract):
    def __init__(self, **kwargs):
        kwargs['big'] = False
        super(Integer, self).__init__(11, **kwargs)


class BigInteger(ColumnIntegerAbstract):
    def __init__(self, **kwargs):
        kwargs['big'] = True
        super(BigInteger, self).__init__(20, **kwargs)


class PositiveInteger(ColumnIntegerAbstract):
    def __init__(self, **kwargs):
        kwargs['big'] = False
        kwargs['unsigned'] = True
        super(PositiveInteger, self).__init__(11, **kwargs)


class PositiveBigInteger(ColumnIntegerAbstract):
    def __init__(self, **kwargs):
        kwargs['big'] = True
        kwargs['unsigned'] = True
        super(PositiveBigInteger, self).__init__(20, **kwargs)


class Float(ColumnFloatAbstract):
    def __init__(self, length=None, decimals=None, **kwargs):
        kwargs['big'] = False
        super(Float, self).__init__(length, decimals, **kwargs)


class BigFloat(ColumnFloatAbstract):
    def __init__(self, length=None, decimals=None, **kwargs):
        kwargs['big'] = True
        super(BigFloat, self).__init__(length, decimals, **kwargs)


class PositiveFloat(ColumnFloatAbstract):
    def __init__(self, length=None, decimals=None, **kwargs):
        kwargs['big'] = False
        kwargs['unsigned'] = True
        super(PositiveFloat, self).__init__(length, decimals, **kwargs)


class PositiveBigFloat(ColumnFloatAbstract):
    def __init__(self, length=None, decimals=None, **kwargs):
        kwargs['big'] = True
        kwargs['unsigned'] = True
        super(PositiveBigFloat, self).__init__(length, decimals, **kwargs)


class Numeric(ColumnNumericAbstract):
    pass


class Currency(ColumnNumericAbstract):
    def __init__(self, currency=None, currency_format=None, **kwargs):
        self.always_with_decimal = kwargs.pop('always_with_decimal', True)
        super(Currency, self).__init__(**kwargs)
        self._currency = currency
        self._format = currency_format

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = value or manager.get_default_currency()
        self._format = manager.get_currency_format(self._currency) if self._currency is not None else None

    @property
    def currency_format(self):
        return self._format

    @currency_format.setter
    def currency_format(self, value):
        if value is None:
            self._format = manager.get_currency_format(self._currency) if self._currency is not None else None
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise OrmValueError("currency format must be set using tuple of full and integer representations!")
        self._format = value

    @property
    def full_format(self):
        return "%i.%d" if self._format is None else self._format[0]

    @property
    def integer_format(self):
        return "%i" if self._format is None else self._format[1]

    def text_repr(self, value, instance=None):
        if value is None:
            return ""
        if not isinstance(value, (int, float)):
            raise OrmValueError("currency expects (float|int|None) type of value to be given!")
        value = float(value)
        use_full_format = self.always_with_decimal or not value.is_integer()
        format_ = self.full_format if use_full_format else self.integer_format
        i, d = divmod(value, 1)
        return format_.replace("%i", str(int(round(i)))).replace("%d", "%02d" % str(int(round(d * 100))))


class PositiveNumeric(ColumnNumericAbstract):
    def __init__(self, length, decimals, **kwargs):
        kwargs['unsigned'] = True
        super(PositiveNumeric, self).__init__(length, decimals, **kwargs)


class String(ColumnStringAbstract):
    pass


class Label(String):
    def __init__(self, length=250, **kwargs):
        kwargs['nullable'] = kwargs.get('nullable', False)
        kwargs['default'] = kwargs.get('default', '')
        kwargs['required'] = True
        kwargs['max_chars'] = length
        kwargs['findable'] = True
        super(Label, self).__init__(length, **kwargs)


class CaptionString(String):
    def __init__(self, length=60, caption=None, abbreviation=None, **kwargs):
        kwargs['nullable'] = kwargs.get('nullable', False)
        kwargs['default'] = kwargs.get('default', '')
        kwargs['required'] = True
        kwargs['is_caption_key'] = True
        kwargs['max_chars'] = length
        kwargs['findable'] = True
        kwargs['caption'] = caption or kwargs.get('caption', None)
        kwargs['abbreviation'] = abbreviation or kwargs.get('abbreviation', None)
        super(CaptionString, self).__init__(length, **kwargs)


class Uuid(String):
    """ UUID data type to store unique values, basing on Python's UUID4 function. """

    def __init__(self, **kwargs):
        kwargs['strict_find'] = True
        super(Uuid, self).__init__(36, **kwargs)

    @staticmethod
    def _make_uuid():
        return str(uuid.uuid4())

    def verify(self, value):
        value = super(Uuid, self).verify(value)
        if value is None:
            return None
        value = str(value).replace('-', '').lower()
        if re.sub("[^0-9a-f]", "", value) != value:
            raise OrmValueVerificationError(gettext("Must be valid UUID"))
        if len(value) != 32:
            raise OrmValueVerificationError(gettext("Must be valid UUID"))
        return "%s-%s-%s-%s-%s" % (value[0:8], value[8:12], value[12:16], value[16:20], value[20:])


class Text(ColumnTextAbstract):
    pass


class LongText(ColumnTextAbstract):
    def __init__(self, **kwargs):
        kwargs['big'] = True
        super(LongText, self).__init__(**kwargs)


class Boolean(ColumnBooleanAbstract):
    @staticmethod
    def _getter(instance, key):
        value = instance.__getattrabs__(key)
        if isinstance(value, str):
            return value
        # return None if value is None else bool(value)
        return value

    def __init__(self, **kwargs):
        kwargs['getter'] = kwargs.get('getter', self._getter)
        kwargs['nullable'] = kwargs.get('nullable', False)
        kwargs['options'] = {
            1: kwargs.get('caption_yes', None) or gettext('Yes'),
            0: kwargs.get('caption_no', None) or gettext('No')
        }
        super(Boolean, self).__init__(**kwargs)

    def verify(self, value):
        value = super(Boolean, self).verify(value)
        if value is None:
            return None
        if isinstance(value, str) \
                and (value.lower() in (
                    gettext('No').lower(),
                    gettext('Off').lower(),
                    gettext('Disable').lower(),
                    gettext('False').lower(),
                    'n',
                    'f',
                ) or value.lower()[0] in ('n', 'f')):
            return False
        return bool(value)


class Date(ColumnDateAbstract):
    def __init__(self, **kwargs):
        super(Date, self).__init__(**kwargs)


class Time(ColumnTimeAbstract):
    def __init__(self, fsp=None, **kwargs):
        self._hasdate = False
        self._hastime = True
        super(Time, self).__init__(fsp, **kwargs)


class DateTime(ColumnDatetimeAbstract):
    def __init__(self, fsp=None, **kwargs):
        self._hasdate = True
        self._hastime = True
        super(DateTime, self).__init__(fsp, **kwargs)


class Blob(ColumnBlobAbstract):
    def __init__(self, **kwargs):
        kwargs['big'] = False
        super(Blob, self).__init__(**kwargs)


class LongBlob(ColumnBlobAbstract):
    def __init__(self, **kwargs):
        kwargs['big'] = True
        super(LongBlob, self).__init__(**kwargs)


class UuidPrimaryKey(Uuid):
    def __init__(self, **kwargs):
        kwargs['primary_key'] = True
        kwargs['nullable'] = False
        kwargs['default'] = self._make_uuid
        super(UuidPrimaryKey, self).__init__(**kwargs)
        self.base_type = Uuid


class AutoIncrement(PositiveInteger):
    def __init__(self, **kwargs):
        kwargs['auto_increment'] = True
        kwargs['primary_key'] = True
        kwargs['nullable'] = False
        super(AutoIncrement, self).__init__(**kwargs)
        self.base_type = PositiveInteger


class BigAutoIncrement(PositiveBigInteger):
    def __init__(self, **kwargs):
        kwargs['auto_increment'] = True
        kwargs['primary_key'] = True
        kwargs['nullable'] = False
        super(BigAutoIncrement, self).__init__(**kwargs)
        self.base_type = PositiveBigInteger


class ObjectVersion(PositiveInteger):
    def __init__(self, **kwargs):
        kwargs['is_version_key'] = True
        kwargs['default'] = kwargs.get('default', 1)
        kwargs['nullable'] = kwargs.get('nullable', False)
        super(ObjectVersion, self).__init__(**kwargs)


class ObjectVersionTimestamp(DateTime):
    def __init__(self, **kwargs):
        kwargs['is_version_key'] = True
        super(ObjectVersionTimestamp, self).__init__(**kwargs)

    def on_model_declared(self):
        self.model.__meta__.timestamp_modification.append(self)


class ObjectSoftdeleteAndVersion(Integer):
    def __init__(self, **kwargs):
        kwargs['is_version_key'] = True
        kwargs['default'] = kwargs.get('default', 1)
        kwargs['nullable'] = True
        kwargs['is_softdelete_key'] = True
        super(ObjectSoftdeleteAndVersion, self).__init__(**kwargs)


class SoftdeleteTimestamp(DateTime):
    def __init__(self, **kwargs):
        kwargs['is_softdelete_key'] = True
        super(SoftdeleteTimestamp, self).__init__(**kwargs)


class SoftdeleteBoolean(Boolean):
    def __init__(self, **kwargs):
        kwargs['is_softdelete_key'] = True
        super(SoftdeleteBoolean, self).__init__(**kwargs)


class SoftdeleteDate(Date):
    def __init__(self, **kwargs):
        kwargs['is_softdelete_key'] = True
        super(SoftdeleteDate, self).__init__(**kwargs)


class CreationTimestamp(DateTime):
    def __init__(self, **kwargs):
        kwargs['default'] = datetime.datetime.now
        super(CreationTimestamp, self).__init__(**kwargs)

    def on_model_declared(self):
        self.model.__meta__.timestamp_creation.append(self)


class ModificationTimestamp(DateTime):
    def __init__(self, **kwargs):
        kwargs['default'] = datetime.datetime.now
        super(ModificationTimestamp, self).__init__(**kwargs)

    def on_model_declared(self):
        self.model.__meta__.timestamp_modification.append(self)


class Password(String):
    @staticmethod
    def _is_password_strong(value):
        l_ = len(value)
        vn = ''.join(list((filter(lambda x: not x.isdigit(), value))))
        if len(vn) == l_ or len(vn) == 0:
            return False
        return True

    def _setter(self, instance, key, value, on_instance_loaded=False):
        if on_instance_loaded:
            instance.__setattrvalue__(key, value)
            return value
        if not value:
            if self.empty is False:
                raise OrmProhibittedValueSet()
            else:
                instance.__setattrvalue__(key, self.empty)
                return self.empty
        if self.strong and not self._is_password_strong(value):
            raise OrmPasswordIsWeak(
                "The password is about to set to the `Password` attribute is too weak: '%s'!" % str(value)
            )
        value += self.salt
        if self.encryption == 'plain':
            instance.__setattrvalue__(key, value)
            return value
        elif self.encryption == 'md5':
            value_ = hashlib.md5(value.encode('utf-8')).hexdigest().lower()
        elif self.encryption == 'sha1':
            value_ = hashlib.sha1(value.encode('utf-8')).hexdigest().lower()
        elif self.encryption == 'sha224':
            value_ = hashlib.sha224(value.encode('utf-8')).hexdigest().lower()
        elif self.encryption == 'sha256':
            value_ = hashlib.sha256(value.encode('utf-8')).hexdigest().lower()
        elif self.encryption == 'sha384':
            value_ = hashlib.sha384(value.encode('utf-8')).hexdigest().lower()
        elif self.encryption == 'sha512':
            value_ = hashlib.sha512(value.encode('utf-8')).hexdigest().lower()
        else:
            value_ = None
        instance.__setattrvalue__(key, value_)
        return value_

    @staticmethod
    def _text_repr(void):
        return "******"

    def __init__(self, *args, **kwargs):
        length = None
        encryption = None
        for arg in args:
            if isinstance(arg, int) and arg > 0:
                length = arg
            elif isinstance(arg, str) \
                    and arg.lower() in ('plain', 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'):
                encryption = arg.lower()
            else:
                AttributeError("Unknown value given for `Password`: %s" % str(arg))
        encryption = str(kwargs.get('encryption', 'sha256')).lower() if encryption is None else encryption
        if encryption not in ('plain', 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'):
            raise AttributeError(
                "`Password` attribute supports only next encryption algorithms:"
                " 'plain', 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'!"
            )
        length = kwargs.get('length', None) if length is None else length
        salt = str(kwargs.get('salt')) if kwargs.get('salt', None) else ''
        empty = kwargs.get('empty', False)
        if empty not in (False, None, ''):
            raise AttributeError("`Password`.`empty` mght be False, None or empty string ('') only!")
        strong = bool(kwargs.get('strong', False))
        if length and length > 255:
            raise AttributeError("`Password` attribute supports maximum 255 chars length of column!")
        if length is None:
            if encryption == 'plain':
                length = 255
            elif encryption == 'md5':
                length = 32
            elif encryption == 'sha1':
                length = 40
            elif encryption == 'sha224':
                length = 56
            elif encryption == 'sha256':
                length = 64
            elif encryption == 'sha384':
                length = 96
            elif encryption == 'sha512':
                length = 128
        nullable = empty is not False
        default = None if nullable else ''
        kwargs['nullable'] = nullable
        kwargs['default'] = default
        kwargs['listable'] = False
        kwargs['findable'] = False
        kwargs['setter'] = self._setter
        kwargs['on_text_repr'] = self._text_repr
        kwargs['on_log_repr'] = str(gettext('Changed'))
        super(Password, self).__init__(length, **kwargs)
        self.value_class = ValuePassword
        self.salt = salt
        self.empty = empty
        self.strong = strong
        self.encryption = encryption
        if encryption == 'plain':
            self.collate = 'utf8_bin'

    def corresponds_to_(self, plain):
        """ Used in SELECT requests, comparing given 'plain' textual password with corresponding
        hashed value stored in the database. """
        if plain is None or isinstance(plain, AttributeValueNull):
            return OrmComparator(self, 'ISNULL')
        if self.encryption == 'plain':
            return self.__eq__(plain)
        elif self.encryption == 'md5':
            return self.__eq__(hashlib.md5(plain.encode('utf-8')).hexdigest().lower())
        elif self.encryption == 'sha1':
            return self.__eq__(hashlib.sha1(plain.encode('utf-8')).hexdigest().lower())
        elif self.encryption == 'sha224':
            return self.__eq__(hashlib.sha224(plain.encode('utf-8')).hexdigest().lower())
        elif self.encryption == 'sha256':
            return self.__eq__(hashlib.sha256(plain.encode('utf-8')).hexdigest().lower())
        elif self.encryption == 'sha384':
            return self.__eq__(hashlib.sha384(plain.encode('utf-8')).hexdigest().lower())
        elif self.encryption == 'sha512':
            return self.__eq__(hashlib.sha512(plain.encode('utf-8')).hexdigest().lower())
        return self.__eq__(plain)


class YearMonth(Float):
    def __init__(self, **kwargs):
        super(YearMonth, self).__init__(**kwargs)
        self.enumerable_value = True
        self.value_class = ValueYearMonth
        self.year_first = bool(kwargs.get('year_first', True))
        self.separator = str(kwargs.get('separator', '.'))


class Phone(String):
    def __init__(self,
                 formats=None,
                 format_ext=None,
                 local_prefixes=None,
                 store_local_prefix=True,
                 **kwargs):
        kwargs['nullable'] = kwargs.get('nullable', False)
        kwargs['default'] = kwargs.get('default', '')
        if formats is not None and not isinstance(formats, (list, tuple)):
            raise OrmDefinitionError("Phone attribute's options 'formats' must be a type of list or tuple!")
        elif formats:
            formats_ = dict()
            for f in formats:
                fl = len(f) - len(f.replace('?', ''))
                formats_[fl] = f
        else:
            formats_ = manager.get_telephony_formats()
        if local_prefixes and not isinstance(local_prefixes, dict):
            raise OrmDefinitionError(
                "Phone attribute option 'local_prefixes' must be a type of dict in format"
                " ({<base_length>: <prefix>, <base_length>: <prefix>})"
            )
        super(Phone, self).__init__(63, **kwargs)
        self.enumerable_value = True
        self.value_class = ValuePhone
        self.formats = formats_
        self.format_ext = format_ext if format_ext else manager.get_telephony_format_ext()
        self.local_prefixes = local_prefixes if local_prefixes else manager.get_telephony_local_prefixes()
        self.store_local_prefix = bool(store_local_prefix)

    def _apply_local_prefix(self, phone):
        if phone is None:
            return None
        plen = len(phone)
        if plen in self.local_prefixes:
            phone = str(self.local_prefixes[plen]) + phone
        return phone

    def do_store_local_prefix(self, phone):
        if phone is None:
            return None
        if not self.store_local_prefix:
            return phone
        plen = len(phone)
        if plen in self.local_prefixes:
            phone = str(self.local_prefixes[plen]) + phone
        return phone

    def format_phone(self, phone, ext):
        if not phone:
            phone = ""
        phone = re.sub("[^0-9]", "", str(phone))
        if phone:
            phone = self._apply_local_prefix(phone)
        plen = len(phone)
        if plen in self.formats:
            fv = self.formats[plen]
            for ch in phone:
                fv = fv.replace('?', ch, 1)
            phone = fv
        if ext:
            ext_ = self.format_ext.replace('?', re.sub("[^0-9]", "", ext))
            phone = "%s%s" % (phone, ext_)
        return phone

    @staticmethod
    def _decompose_phone(value):
        if not value:
            return '', ''
        if ',' in value:
            phone_ext = value.split(',')
            phone = phone_ext[0]
            ext = phone_ext[1]
        else:
            phone = value
            ext = ''
        return phone, ext

    @staticmethod
    def _find_prepare(value):
        if not value:
            return value
        return re.sub("[^0-9]", "", str(value))


class Email(String):
    def __init__(self, **kwargs):
        kwargs['nullable'] = kwargs.get('nullable', False)
        kwargs['default'] = kwargs.get('default', '')
        super(Email, self).__init__(60, **kwargs)

    def verify(self, value):
        value = super(Email, self).verify(value)
        if value is None:
            return None
        if not self.required and not value:
            return ""
        value = str(value).lower()
        if '@' not in value or value.count('@') > 1:
            raise OrmValueVerificationError(gettext("Must be an e-mail address"))
        if re.sub("[^0-9a-z.@\-_+\[\]]", "", value) != value:
            raise OrmValueVerificationError(gettext("Must be an e-mail address"))
        p = value.split('@')
        if not p[0] or not p[1]:
            raise OrmValueVerificationError(gettext("Must be an e-mail address"))
        if '.' not in p[1] or not ('[' in p[1] and ']' in p[1]):
            raise OrmValueVerificationError(gettext("Must be an e-mail address"))
        return value


class IMAddress(String):
    def __init__(self, **kwargs):
        kwargs['nullable'] = kwargs.get('nullable', False)
        kwargs['default'] = kwargs.get('default', '')
        super(IMAddress, self).__init__(120, **kwargs)


class SocialNetworkAddress(String):
    def __init__(self, **kwargs):
        kwargs['nullable'] = kwargs.get('nullable', False)
        kwargs['default'] = kwargs.get('default', '')
        super(SocialNetworkAddress, self).__init__(250, **kwargs)


class IPAddress(ColumnAttributeAbstract):
    def __init__(self, **kwargs):
        kwargs['nullable'] = kwargs.get('nullable', True)
        kwargs['default'] = kwargs.get('default', None)
        kwargs['cast_write'] = self._cast_write
        kwargs['cast_read'] = self._cast_read
        kwargs['cast_order_by'] = None
        kwargs['cast_group_by'] = self._cast_read
        kwargs['strict_find'] = True
        super(IPAddress, self).__init__(**kwargs)
        self.value_class = AttributeValueString

    @staticmethod
    def _cast_write(context, pn):
        if context.session.dbms_type == 'mysql' and context.params[pn] is not None:
            return inet6_aton_(context.params[pn])
        return "%(" + pn + ")s"

    def _cast_read(self, context):
        if context.session.dbms_type == 'mysql':
            return inet6_ntoa_(uncastable_(self))
        elif context.session.dbms_type == 'postgresql':
            return host_(uncastable_(self))
        return self

    def is_eq_with_tbl_schema(self, struct, session):
        if session.dbms_type == 'mysql':
            if str(struct['data_type']).lower() != 'varbinary':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if struct['character_maximum_length'] != 32:
                return False
        elif session.dbms_type == 'postgresql':
            if str(struct['data_type']).lower() != 'inet':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        if session.dbms_type == 'mysql':
            d.append("VARBINARY(32)")
        elif session.dbms_type == 'postgresql':
            d.append("INET")
        else:
            raise TypeError("this column type is not supported for this database and has no alternative!")
        if not self.nullable:
            d.append('NOT NULL')
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            d.append("SET DATA TYPE INET")
            d.append("DROP NOT NULL" if self.nullable else "SET NOT NULL")
            d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)

    def verify(self, value):
        value = super(IPAddress, self).verify(value)
        if value is None:
            return None
        if not self.required and not value:
            return ""
        value = str(value)
        ipvers = ipaddr_version(value)
        if ipvers == 0:
            raise OrmValueVerificationError(gettext("Must be an IP address"))
        return value

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


class IPMask(Integer):
    """ Network IP mask stored at the DBMS side as small integer value between 0 and 128 for
    IPv6, and 0 and 32 for IPv4 (conforming to CIDR specification). So, textual IPv4 mask
    representation as A.B.C.D will be converted to the numeric CIDR anyway, if given. """

    def __init__(self, **kwargs):
        kwargs['nullable'] = kwargs.get('nullable', True)
        kwargs['default'] = kwargs.get('default', None)
        kwargs['unsigned'] = True
        self.prefix_with_slash = bool(kwargs.pop('prefix_with_slash', False))
        super(IPMask, self).__init__(**kwargs)

    def verify(self, value):
        value = super(IPMask, self).verify(value)
        if value is None:
            return None
        if not isinstance(value, (int, str)):
            raise OrmValueError("IPMask can be set using (str|int) type only!")
        if isinstance(value, int):
            if value < 0 or value > 128:
                raise OrmValueVerificationError(gettext("Must be a network mask"))
            return value
        ipvers = ipaddr_version(value)
        if ipvers != 4:
            raise OrmValueVerificationError(gettext("Must be a network mask"))
        return int(ipv4mask_2_cidr(value))

    def text_repr(self, value, instance=None):
        if value is None:
            return ""
        return "/%i" % int(value) if self.prefix_with_slash else str(value)


class MACAddress(String):
    def __init__(self, **kwargs):
        kwargs['nullable'] = kwargs.get('nullable', True)
        kwargs['default'] = kwargs.get('default', None)
        kwargs['cast_write'] = self._cast_write
        kwargs['cast_read'] = self._cast_read
        kwargs['cast_order_by'] = None
        kwargs['cast_group_by'] = self._cast_read
        kwargs['strict_find'] = True
        self.word_sz = kwargs.pop('word_sz', 2)
        self.separator = kwargs.pop('separator', ':')
        super(MACAddress, self).__init__(16, **kwargs)
        self.value_handler = self._value_handler

    @staticmethod
    def _cast_write(context, pn):
        value = context.params[pn]
        if value is None:
            return "NULL"
        value = re.sub("[^0-9a-f]", "", str(value).lower())
        sz = len(value)
        if sz < 12:
            value = "%s%s" % ("0" * (12 - sz), value)
        return '"%s"' % str(value)

    def _cast_read(self, context):
        return concat_ws_(
            self.separator,
            substr_(uncastable_(self), 1, 4),
            substr_(uncastable_(self), 5, 4),
            substr_(uncastable_(self), 9, 4)
        ) if self.word_sz == 4 else concat_ws_(
            self.separator,
            substr_(uncastable_(self), 1, 2),
            substr_(uncastable_(self), 3, 2),
            substr_(uncastable_(self), 5, 2),
            substr_(uncastable_(self), 7, 2),
            substr_(uncastable_(self), 9, 2),
            substr_(uncastable_(self), 11, 2),
        )

    def _format_value(self, value):
        value = re.sub("[^0-9a-f]", "", str(value).lower())
        sz = len(value)
        if sz < 12:
            value = "%s%s" % ("0" * (12 - sz), value)
        return "%s%s%s%s%s" % (
            value[0:4], self.separator,
            value[4:8], self.separator,
            value[8:12]) \
            if self.word_sz == 4 else \
            "%s%s%s%s%s%s%s%s%s%s%s" % (
                value[0:2], self.separator,
                value[2:4], self.separator,
                value[4:6], self.separator,
                value[6:8], self.separator,
                value[8:10], self.separator,
                value[10:12]
            )

    def _value_handler(self, value):
        if value is None:
            return None if self.nullable else self._format_value('000000000000')
        return self._format_value(value)


class IPRequesties(ColumnAttributeAbstract):
    def __init__(self, **kwargs):
        kwargs['nullable'] = kwargs.get('nullable', True)
        kwargs['default'] = kwargs.get('default', None)
        kwargs['cast_write'] = self._cast_write
        kwargs['cast_read'] = self._cast_read
        kwargs['cast_order_by'] = None
        kwargs['cast_group_by'] = self._cast_read
        kwargs['strict_find'] = True
        self.default_v4mask = kwargs.pop('default_v4mask', 32)
        self.default_v6prefix = kwargs.pop('default_v6prefix', 64)
        # self.hide_host_mask = kwargs.pop('hide_host_mask', True)
        # TODO! '_cast_read()' with 'hide_host_mask' parameter (for MySQL implementation)
        self.hide_host_mask = False
        super(IPRequesties, self).__init__(**kwargs)
        self.enumerable_value = True
        self.value_class = ValueIPRequesties

    @staticmethod
    def _cast_write(context, pn):
        value = context.params[pn]
        if isinstance(value, str):
            return "%(" + pn + ")s"
        if value is None or isinstance(value, AttributeValueNull):
            return "NULL"
        if isinstance(value, ValueIPRequesties) and value.null:
            return "NULL"
        if context.session.dbms_type == 'mysql':
            return concat_(inet6_aton_(value.ipaddr), unhex_("%X" % int(value.ipmask)))
        context.params[pn] = value.string
        return "%(" + pn + ")s"

    def _cast_read(self, context):
        if context.session.dbms_type == 'mysql':
            return if_(
                length_(uncastable_(self)) == 17,
                concat_(
                    inet6_ntoa_(substr_(uncastable_(self), 1, 16)),
                    '/',
                    conv_(hex_(substr_(uncastable_(self), 17, 1)), 16, 10)
                ),
                concat_(
                    inet6_ntoa_(substr_(uncastable_(self), 1, 4)),
                    '/',
                    conv_(hex_(substr_(uncastable_(self), 5, 1)), 16, 10)
                )
            )
        elif context.session.dbms_type == 'postgresql':
            if self.hide_host_mask:
                return self
            else:
                return pg_text_(uncastable_(self))
        return self

    def is_eq_with_tbl_schema(self, struct, session):
        if session.dbms_type == 'mysql':
            if str(struct['data_type']).lower() != 'varbinary':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
            if struct['character_maximum_length'] != 64:
                return False
        elif session.dbms_type == 'postgresql':
            if str(struct['data_type']).lower() != 'inet':
                return False
            if struct['is_nullable'] != self.nullable:
                return False
        return True

    def declaration_sql(self, session):
        d = list()
        if session.dbms_type == 'mysql':
            d.append("VARBINARY(64)")
        elif session.dbms_type == 'postgresql':
            d.append("INET")
        else:
            raise TypeError("this column type is not supported for this database and has no alternative!")
        if not self.nullable:
            d.append('NOT NULL')
        return " ".join(d)

    def alter_sql(self, session):
        if session.dbms_type == 'postgresql':
            d = list()
            d.append("SET DATA TYPE INET")
            d.append("DROP NOT NULL" if self.nullable else "SET NOT NULL")
            d.append("DROP DEFAULT")
            return d
        return self.declaration_sql(session)


class GeometryAbstract(String):
    def __init__(self, **kwargs):
        kwargs['strict_find'] = True
        self.decimals = kwargs.pop('decimals', 0)
        super(GeometryAbstract, self).__init__(**kwargs)
        self.enumerable_value = True


class Dimensions2D(GeometryAbstract):
    def __init__(self, **kwargs):
        super(Dimensions2D, self).__init__(**kwargs)
        self.value_class = ValueDimensions2D


class Dimensions3D(GeometryAbstract):
    def __init__(self, **kwargs):
        super(Dimensions3D, self).__init__(**kwargs)
        self.value_class = ValueDimensions3D


class Box(GeometryAbstract):
    def __init__(self, **kwargs):
        super(Box, self).__init__(**kwargs)
        self.value_class = ValueBox


class Point(GeometryAbstract):
    def __init__(self, **kwargs):
        super(Point, self).__init__(**kwargs)
        self.value_class = ValuePoint


class Vector(GeometryAbstract):
    def __init__(self, **kwargs):
        super(Vector, self).__init__(**kwargs)
        self.value_class = ValueVector


class GeoCoordinate(GeometryAbstract):
    def __init__(self, **kwargs):
        super(GeoCoordinate, self).__init__(**kwargs)
        self.value_class = ValueGeoCoordinate


class IntegerChoice(Integer):
    def __init__(self, options, **kwargs):
        if not isinstance(options, dict):
            raise OrmParameterError("IntegerChoice requires 'options' argument to be a type (dict)!")
        if 'default' not in kwargs:
            raise OrmParameterError("IntegerChoice requires 'default' to be set!")
        kwargs['options'] = options
        super(IntegerChoice, self).__init__(**kwargs)

    def verify(self, value):
        if value not in self.options:
            raise OrmValueVerificationError("Unacceptable choice")
        value = super(IntegerChoice, self).verify(value)
        if value is None:
            return None
        return value


class StringChoice(String):
    def __init__(self, options, **kwargs):
        if not isinstance(options, dict):
            raise OrmParameterError("StringChoice requires 'options' argument to be a type (dict)!")
        if 'default' not in kwargs:
            raise OrmParameterError("StringChoice requires 'default' to be set!")
        kwargs['options'] = options
        super(StringChoice, self).__init__(**kwargs)

    def verify(self, value):
        if value not in self.options:
            raise OrmValueVerificationError("Unacceptable choice")
        value = super(StringChoice, self).verify(value)
        if value is None:
            return None
        return value


