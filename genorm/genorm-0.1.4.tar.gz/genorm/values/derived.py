import math
import re
import hashlib
from pc23 import xrange
from .base import AttributeValueVirtual, AttributeValueNull, AttributeValueString
from ..exceptions import OrmValueError, OrmAttributeTypeMistake
from ..utils import ipaddr_version, ipv4mask_2_cidr


class ValuePassword(AttributeValueString):
    def try_password(self, password):
        value = self.value
        if value is None or isinstance(value, AttributeValueNull):
            return password is None or isinstance(password, AttributeValueNull)
        encryption = self.c.encryption
        if encryption == 'plain':
            trying = password
        elif encryption == 'md5':
            trying = hashlib.md5(password.encode('utf-8')).hexdigest().lower()
        elif encryption == 'sha1':
            trying = hashlib.sha1(password.encode('utf-8')).hexdigest().lower()
        elif encryption == 'sha224':
            trying = hashlib.sha224(password.encode('utf-8')).hexdigest().lower()
        elif encryption == 'sha256':
            trying = hashlib.sha256(password.encode('utf-8')).hexdigest().lower()
        elif encryption == 'sha384':
            trying = hashlib.sha384(password.encode('utf-8')).hexdigest().lower()
        elif encryption == 'sha512':
            trying = hashlib.sha512(password.encode('utf-8')).hexdigest().lower()
        else:
            trying = None
        return value == trying


class ValueYearMonth(AttributeValueVirtual):
    basecls = False
    check_modified = True

    def __init__(self, value):
        super(ValueYearMonth, self).__init__()
        self._value = value

    def __repr__(self):
        if self.null:
            return "<NULL>"
        y, m = self._decompose()
        c = self._get_c()
        if c is None:
            return self._value
        r = (str("%04d" % y), str("%02d" % m)) if c.year_first else (str("%04d" % m), str("%02d" % y))
        return self.c.separator.join(r)

    def base(self, value):
        return None if value is None or isinstance(value, AttributeValueNull) else float(value)

    @property
    def value(self):
        return None if self._value is None else float(self._value)

    @property
    def string(self):
        if self.null:
            return ""
        return self.__repr__()

    def _get_c(self):
        return getattr(self.instance.__class__, self.model_k) if self.model_k is not None else None

    def _decompose(self):
        y, m = divmod(self._value, 1)
        return int(round(y)), int(round(m*100))

    def get_value(self):
        return self

    @property
    def year(self):
        return None if self._value is None else self._decompose()[0]

    @year.setter
    def year(self, value):
        if value is None or isinstance(value, AttributeValueNull):
            value = 0
        y, m = self._decompose() if not self.null else (0, 0)
        y = value
        self._value = float(y) + (float(m) / 100)

    @property
    def month(self):
        return None if self._value is None else self._decompose()[0]

    @month.setter
    def month(self, value):
        if value is None or isinstance(value, AttributeValueNull):
            value = 0
        y, m = self._decompose() if not self.null else (0, 0)
        m = value
        self._value = float(y) + (float(m) / 100)

    @property
    def year_month(self):
        return None if self.null else self._decompose()

    @property
    def null(self):
        return self._value is None

    @null.setter
    def null(self, value):
        if bool(value):
            c = self._get_c()
            if c is not None and not c.nullable:
                raise OrmValueError("cannot be NULL because this attribute is not nullable!")
            self._value = None
        else:
            self._value = 0.0

    def set_value(self, instance, key, value):
        before_ = self._value
        if isinstance(value, ValueYearMonth):
            if value.null:
                self.null = True
            else:
                self.null = False
                self.year, self.month = value.year_month
            return self._value, before_
        if value is None or isinstance(value, AttributeValueNull):
            c = self._get_c()
            if c is not None and not c.nullable:
                raise OrmValueError("cannot be NULL because this attribute is not nullable!")
            self._value = None
            return self._value, before_
        if isinstance(value, float):
            self._value = value
            return self._value, before_
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise OrmValueError(
                "YearMonth requires that value to be set using [Year, Month] format or using '.month' and"
                " '.year' properties!"
            )
        self.year = value[0]
        self.month = value[1]
        return self._value, before_


class ValuePhone(AttributeValueVirtual):
    basecls = False
    check_modified = True

    def __init__(self, value):
        super(ValuePhone, self).__init__()
        self._value = value

    def __repr__(self):
        if self.null:
            return "<NULL>"
        return self._format_phone()

    def base(self, value):
        return None if value is None or isinstance(value, AttributeValueNull) else str(value)

    @property
    def value(self):
        return self._value

    @property
    def string(self):
        if self.null:
            return ""
        return self.__repr__()

    def _get_c(self):
        return getattr(self.instance.__class__, self.model_k) if self.model_k is not None else None

    def _format_phone(self):
        if self._value is None:
            return ""
        c = self._get_c()
        return c.format_phone(*self._decompose()) if c is not None else self._value

    def _decompose(self):
        if self._value is None:
            return None
        if "," not in self._value:
            return self._value, None
        return self._value.split(",")

    def get_value(self):
        return self

    @property
    def null(self):
        return self._value is None

    @null.setter
    def null(self, value):
        if bool(value):
            c = self._get_c()
            if c is not None and not c.nullable:
                raise OrmValueError("cannot be NULL because this attribute is not nullable!")
            self._value = None
        else:
            self._value = 0.0

    def clear(self):
        c = self._get_c()
        self._value = None if c is not None and c.nullable else ""

    @property
    def phone(self):
        if self._value is None:
            return None
        return self._decompose()[0]

    @property
    def ext(self):
        if self._value is None:
            return None
        return self._decompose()[1]

    @phone.setter
    def phone(self, value):
        c = self._get_c()
        if c is None:
            return
        phone, ext = self._decompose() if self._value else (None, None)
        phone = self.c.do_store_local_prefix(re.sub("[^0-9]", "", str(value)))
        r = phone
        if ext:
            r += "," + str(ext)
        self._value = r

    @ext.setter
    def ext(self, value):
        phone, ext = self._decompose() if self._value else (None, None)
        if not value:
            self._value = phone
            return
        ext = re.sub("[^0-9]", "", str(value))
        if not phone:
            phone = ""
        self._value = "%s,%s" % (str(phone), str(ext))

    def set_value(self, instance, key, value):
        before_ = self._value
        if isinstance(value, ValuePhone):
            self.phone, self.ext = value.phone, value.ext
            return self._value, before_
        if value is None:
            self.clear()
            return self._value, before_
        if isinstance(value, (list, tuple)):
            if len(value) > 2:
                raise OrmValueError("Phone attribute can be set to (str) or (list|tuple) of length 1 or 2!")
            if len(value) == 2:
                self.phone, self.ext = value
            else:
                self.phone, self.ext = value[0], None
            return self._value, before_
        elif isinstance(value, str):
            if ',' in value:
                pc = value.split(',')
                if len(pc) > 2:
                    raise OrmValueError(
                        "(str) value for Phone attribute when set might contain comma as delimiter"
                        " for ext.phone, but only one! More than one been given: '%s'!" % str(value)
                    )
                if len(pc) == 2:
                    self.phone, self.ext = pc
                else:
                    self.phone, self.ext = pc[0], None
                return self._value, before_
            else:
                self.phone, self.ext = value, None
                return self._value, before_
        elif isinstance(value, int):
            self.phone, self.ext = str(value), None
            return self._value, before_
        else:
            raise OrmValueError("value for Phone can be type of (str|list|tuple) only!")


class ValueIPRequesties(AttributeValueVirtual):
    basecls = False
    check_modified = True

    def __init__(self, value):
        super(ValueIPRequesties, self).__init__()
        self._ipaddr = None
        self._ipmask = None
        self._set(value)

    def __repr__(self):
        if self.null:
            return "<NULL>"
        return self._str()

    def base(self, value):
        return None if self.null else self.value

    @property
    def value(self):
        return self
        # return None if self.null else self._str()

    @property
    def string(self):
        return self._str()

    def _get_c(self):
        return getattr(self.instance.__class__, self.model_k) if self.model_k is not None else None

    def get_value(self):
        return self

    @property
    def null(self):
        return self._ipaddr is None

    @null.setter
    def null(self, value):
        if bool(value):
            c = self._get_c()
            if c is not None and not c.nullable:
                raise OrmValueError("cannot be NULL because this attribute is not nullable!")
            self._ipaddr = None
        else:
            self.ipaddr, self.ipmask = '0.0.0.0', 0

    def _str(self):
        if self.null:
            return ""
        return self._repr()

    def _repr(self):
        if self.null:
            return None
        c = self._get_c()
        if c is None:
            return "%s/%s" % (str(self._ipaddr), str(self._ipmask))
        r = [str(self._ipaddr), ]
        if not self._is_host_addr() or not c.hide_host_mask:
            r.append(str(self._ipmask))
        return "/".join(r)

    def _is_host_addr(self):
        if self.null:
            return True
        ipvers = ipaddr_version(self._ipaddr)
        return self._ipmask == 32 if ipvers == 4 else (self._ipmask == 128 or self._ipmask == 64)

    @staticmethod
    def _verify_ipaddr(value):
        if value is None or isinstance(value, AttributeValueNull):
            return None
        ipvers = ipaddr_version(value)
        if not ipvers:
            raise OrmValueError("IPRequesties requires correct IP address to be given, '%s' got!" % str(value))
        return str(value)

    def _verify_ipmask(self, value, ipaddr=None):
        ipaddr_ = ipaddr or self._ipaddr
        if ipaddr_ is None or isinstance(ipaddr_, AttributeValueNull):
            return None
        ipvers = ipaddr_version(ipaddr_)
        c = self._get_c()
        if (value is None or isinstance(value, AttributeValueNull)) and ipaddr_ is not None:
            if c is not None:
                value = c.default_v6prefix if ipvers == 6 else c.default_v4mask
            else:
                value = 0
        if not isinstance(value, (str, int)):
            raise OrmValueError("IPRequesties requires that IP mask be given using (int|str) type!")
        if ipvers == 6 and not isinstance(value, int) and not str(value).isdigit():
            raise OrmValueError("IPRequesties requires that IPv6 prefix be a number!")
        if ipvers == 4:
            ipprefix = ipv4mask_2_cidr(value) \
                if not isinstance(value, int) and not str(value).isdigit() \
                else int(value)
            if ipprefix < 0:
                raise OrmValueError("IPRequesties requires that IPv4 mask cidr be >= 0!")
            if ipprefix > 32:
                raise OrmValueError("IPRequesties requires that IPv4 mask cidr be <= 32!")
        else:
            ipprefix = int(value)
            if ipprefix < 0:
                raise OrmValueError("IPRequesties requires that IPv6 prefix be >= 0!")
            if ipprefix > 128:
                raise OrmValueError("IPRequesties requires that IPv6 prefix be <= 128!")
        return int(ipprefix)

    def _verify(self, ipaddr, ipmask):
        if ipaddr is None or isinstance(ipaddr, AttributeValueNull):
            return None, None
        if not isinstance(ipaddr, str):
            raise OrmValueError("IPRequesties requires IP address to be a string, '%s' got!" % str(type(ipaddr)))
        ipaddr_ = self._verify_ipaddr(ipaddr)
        ipmask_ = self._verify_ipmask(ipmask, ipaddr_)
        return ipaddr_, ipmask_

    def _set(self, value):
        if value is None or isinstance(value, AttributeValueNull):
            self.null = True
            return
        elif isinstance(value, str):
            if '/' not in value:
                ipaddr = value
                ipmask = None
            elif value.count('/') > 1:
                raise OrmValueError("IPRequesties requires 'ipaddr/ipmask' format when list|tuple is used!")
            else:
                ipaddr, ipmask = value.split('/')
        elif not isinstance(value, (list, tuple)):
            ipaddr = value
            ipmask = None
        elif len(value) > 2:
            raise OrmValueError("IPRequesties requires [ipaddr, ipmask] format when list|tuple is used!")
        else:
            ipaddr, ipmask = value
        if ipaddr is None or isinstance(ipaddr, AttributeValueNull):
            self.null = True
            return
        if not isinstance(ipaddr, str):
            raise OrmValueError("IPRequesties requires that IP address to be a (str) type!")
        ipaddr_, ipmask_ = self._verify(ipaddr, ipmask)
        if ipaddr_ is None or isinstance(ipaddr_, AttributeValueNull):
            self.null = True
            return
        self._ipaddr, self._ipmask = ipaddr_, ipmask_

    @property
    def ipaddr(self):
        return self._ipaddr

    @property
    def ipmask(self):
        return self._ipmask

    @property
    def ipreq(self):
        return (self._ipaddr, self._ipmask) if not self.null else (None, None)

    @ipaddr.setter
    def ipaddr(self, value):
        if value is None or isinstance(value, AttributeValueNull):
            self.null = True
            return
        self._ipaddr = self._verify_ipaddr(value)

    @ipmask.setter
    def ipmask(self, value):
        if self.null:
            raise OrmValueError("cannot set IP mask or prefix without IP address defined!")
        self._ipmask = self._verify_ipmask(value)

    def set_value(self, instance, key, value):
        before_ = self._repr()
        if isinstance(value, ValueIPRequesties):
            if value.null:
                self.null = True
            else:
                self.null = False
                self.ipaddr, self.ipmask = value.ipreq
            return self._repr(), before_
        if value is None or isinstance(value, AttributeValueNull):
            c = self._get_c()
            if c is not None and not c.nullable:
                raise OrmValueError("cannot be NULL because this attribute is not nullable!")
            self.null = True
            return self._repr(), before_
        self._set(value)
        return self._repr(), before_


class ValueGeometryAbstract(AttributeValueVirtual):
    basecls = False
    check_modified = True

    def __init__(self, value):
        super(ValueGeometryAbstract, self).__init__()
        self._value = value
        self._geometry = list()
        self._length = 0
        self._separator = 'x'
        self._space_edging = True

    def __repr__(self):
        if self.null:
            return "<NULL>"
        return self._value

    def base(self, value):
        return None if value is None or isinstance(value, AttributeValueNull) else str(value)

    def _set_geom_length(self, value):
        self._length = value
        self._reset_geometry()

    @property
    def value(self):
        return self._value

    @property
    def string(self):
        if self.null:
            return ""
        return self.__repr__()

    def _get_c(self):
        return getattr(self.instance.__class__, self.model_k) if self.model_k is not None else None

    def get_value(self):
        return self

    def _cast_geom_value(self, value):
        c = self._get_c()
        if c is None:
            return str(value)
        if isinstance(value, int):
            return str(value) if not c.decimals else str(("%0."+str(c.decimals)+"f") % float(value))
        if isinstance(value, str):
            try:
                value = float(value.strip())
            except ValueError:
                raise OrmValueError("geometry value must be a type of (int) or (float)!")
        if isinstance(value, float):
            return str(int(round(value))) if not c.decimals else str(("%0."+str(c.decimals)+"f") % float(value))
        raise OrmValueError("geometry value must be a type of (int) or (float)!")

    def _get_geom_part(self, i):
        if i >= len(self._geometry):
            raise OrmAttributeTypeMistake("requested geometry exceeds existing format!")
        if self.null:
            return None
        value = self._geometry[i]
        c = self._get_c()
        if c is None:
            return value
        if c.decimals == 0:
            return int(value)
        else:
            return float(value)

    def _set_geom_part(self, i, value):
        if i >= len(self._geometry):
            raise OrmAttributeTypeMistake("requested geometry exceeds existing format!")
        before_ = self._value
        if self.null:
            self._clear_to_zero()
        self._geometry[i] = self._cast_geom_value(value)
        self._compose_value_from_geometry()
        self.instance.__check_modified__(self.model_k, (self._value, before_))

    def _reset_geometry(self):
        c = self._get_c()
        v = '0' if c is None else ('0' if c.decimals == 0 else str(("%0."+str(c.decimals)+"f") % float(0.0)))
        self._geometry = list()
        for i in xrange(self._length):
            self._geometry.append(v)

    def _compose_value_from_geometry(self):
        sep = " %s " % str(self._separator) if self._space_edging else str(self._separator)
        self._value = sep.join(self._geometry)

    def _set_from_geometry(self, value):
        self._reset_geometry()
        if value is None:
            self._value = None
            return
        if not isinstance(value, (list, tuple)):
            raise OrmValueError("geometry must be set using (list|tuple) type!")
        if len(value) == 0:
            value = list('0' * self._length)
        if len(value) > self._length:
            value = value[:self._length]
        for i in xrange(len(value)):
            self._geometry[i] = self._cast_geom_value(value[i])
        self._compose_value_from_geometry()

    def _clear_to_zero(self):
        self._set_from_geometry([])

    @property
    def null(self):
        return self._value is None

    @null.setter
    def null(self, value):
        if bool(value):
            c = self._get_c()
            if c is not None and not c.nullable:
                raise OrmValueError("cannot be NULL because this attribute is not nullable!")
            self._value = None
        else:
            self._clear_to_zero()

    def clear(self):
        c = self._get_c()
        if c is not None and c.nullable:
            self._set_from_geometry(None)
        else:
            self._clear_to_zero()

    @property
    def geometry(self):
        return self._geometry if self._value is not None else None

    @geometry.setter
    def geometry(self, value):
        if not isinstance(value, (list, tuple)):
            raise OrmValueError("geometry must be set using (list|tuple) type!")
        self._set_from_geometry(value)

    def _decompose_raw(self, value):
        value = value.replace('x', '|').replace(',', '|').replace(self._separator, '|')
        str_parts = value.split('|')
        geo_parts = list()
        for p in str_parts:
            geo_parts.append(self._cast_geom_value(re.sub("[^0-9.|\-]", "", str(p))))
        return geo_parts

    def set_value(self, instance, key, value):
        before_ = self._value
        if isinstance(value, ValueGeometryAbstract):
            value = value._value
        if value is None or isinstance(value, AttributeValueNull):
            self.null = True
            return self._value, before_
        if isinstance(value, (list, tuple)):
            self._set_from_geometry(value)
            return self._value, before_
        elif isinstance(value, str):
            if value.strip() == "":
                self._clear_to_zero()
                return self._value, before_
            self._set_from_geometry(self._decompose_raw(value))
            return self._value, before_
        else:
            raise OrmValueError("value for geometry can be type of (str|list|tuple) only!")


class ValueDimensions2D(ValueGeometryAbstract):
    def __init__(self, value):
        super(ValueDimensions2D, self).__init__(value)
        self._set_geom_length(2)

    @property
    def width(self):
        return self._get_geom_part(0)

    @property
    def height(self):
        return self._get_geom_part(1)

    @width.setter
    def width(self, value):
        self._set_geom_part(0, value)

    @height.setter
    def height(self, value):
        self._set_geom_part(1, value)


class ValueDimensions3D(ValueGeometryAbstract):
    def __init__(self, value):
        super(ValueDimensions3D, self).__init__(value)
        self._set_geom_length(3)

    @property
    def width(self):
        return self._get_geom_part(0)

    @property
    def height(self):
        return self._get_geom_part(1)

    @property
    def depth(self):
        return self._get_geom_part(2)

    @width.setter
    def width(self, value):
        self._set_geom_part(0, value)

    @height.setter
    def height(self, value):
        self._set_geom_part(1, value)

    @depth.setter
    def depth(self, value):
        self._set_geom_part(2, value)


class ValuePoint(ValueGeometryAbstract):
    def __init__(self, value):
        super(ValuePoint, self).__init__(value)
        self._separator = ','
        self._space_edging = False
        self._set_geom_length(2)

    @property
    def x(self):
        return self._get_geom_part(0)

    @property
    def y(self):
        return self._get_geom_part(1)

    @x.setter
    def x(self, value):
        self._set_geom_part(0, value)

    @y.setter
    def y(self, value):
        self._set_geom_part(1, value)


class ValueBox(ValueGeometryAbstract):
    def __init__(self, value):
        super(ValueBox, self).__init__(value)
        self._separator = ','
        self._space_edging = False
        self._set_geom_length(4)

    @property
    def top_left(self):
        return self._get_geom_part(0)

    @property
    def top_right(self):
        return self._get_geom_part(1)

    @property
    def bottom_right(self):
        return self._get_geom_part(2)

    @property
    def bottom_left(self):
        return self._get_geom_part(3)

    @top_left.setter
    def top_left(self, value):
        self._set_geom_part(0, value)

    @top_right.setter
    def top_right(self, value):
        self._set_geom_part(1, value)

    @bottom_right.setter
    def bottom_right(self, value):
        self._set_geom_part(2, value)

    @bottom_left.setter
    def bottom_left(self, value):
        self._set_geom_part(3, value)

    @property
    def width(self):
        if self.null:
            return None
        return int(round(abs(self.top_right - self.top_left) + abs(self.bottom_right - self.bottom_left)) / 2)

    @property
    def height(self):
        if self.null:
            return None
        return int(round(abs(self.bottom_left - self.top_left) + abs(self.bottom_right - self.top_right)) / 2)

    @width.setter
    def width(self, value):
        if self.null:
            self.top_left = 0
            self.bottom_left = 0
        self.top_right = self.top_left + value
        self.bottom_right = self.bottom_left + value

    @height.setter
    def height(self, value):
        if self.null:
            self.top_left = 0
            self.bottom_left = 0
        self.bottom_left = self.top_left + value
        self.bottom_right = self.top_right + value

    @property
    def corners(self):
        if self.null:
            return None
        return self._geometry


class ValueVector(ValueGeometryAbstract):
    def __init__(self, value):
        super(ValueVector, self).__init__(value)
        self._separator = ','
        self._space_edging = False
        self._set_geom_length(4)

    @property
    def x1(self):
        return self._get_geom_part(0)

    @property
    def y1(self):
        return self._get_geom_part(1)

    @property
    def x2(self):
        return self._get_geom_part(2)

    @property
    def y2(self):
        return self._get_geom_part(3)

    @property
    def length(self):
        if self.null:
            return None
        a = abs(self.x2 - self.x1)
        b = abs(self.y2 - self.y1)
        return math.sqrt(a**2 + b**2)

    @property
    def start(self):
        if self.null:
            return None
        return self.x1, self.y1

    @property
    def end(self):
        if self.null:
            return None
        return self.x2, self.y2

    @x1.setter
    def x1(self, value):
        self._set_geom_part(0, value)

    @y1.setter
    def y1(self, value):
        self._set_geom_part(1, value)

    @x2.setter
    def x2(self, value):
        self._set_geom_part(2, value)

    @y2.setter
    def y2(self, value):
        self._set_geom_part(3, value)

    @start.setter
    def start(self, value):
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise OrmValueError('Vector.start must be set using list|tuple (x,y)!')
        self.x1, self.y1 = value

    @end.setter
    def end(self, value):
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise OrmValueError('Vector.end must be set using list|tuple (x,y)!')
        self.x2, self.y2 = value

    def _compose_value_from_geometry(self):
        self._value = "(%sx%s),(%sx%s)" % (self._geometry[0], self._geometry[1], self._geometry[2], self._geometry[3])


class ValueGeoCoordinate(ValueGeometryAbstract):
    pass

