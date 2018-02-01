# -*- coding: utf8 -*-
""" Different functions (including MySQL functions mapping) and service classes. """

from .attributes.base import AttributeAbstract, OrmComparatorMixin, OrmComparator
from .exceptions import OrmParameterError, OrmDefinitionError


class UncastableColumn(object):
    """ A virtual class that used in functions when declaring _attrs which are castable itself, to
    prevent recursion when function resolved column which returns a function which resolves an
    argument which is castable column again and again and again. """
    def __init__(self, c):
        self.c = c


class RawSql(object):
    """ A class, used to inform the engine that this is a textual name of the requesting column
    or other textual raw query """
    def __init__(self, value):
        self.value = value


class RequestFilterAbstract(object):
    """ Abstract class used by condition filtering classes like RequestWhere, RequestHaving, etc. """
    def __init__(self, *args):
        if not args:
            raise OrmParameterError("Filter instance require at least one filter to be set!")
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        self.args = list(args)
        if self.args[0] not in ('AND', 'OR'):
            self.args = and_(*self.args)

    def extend_with(self, *args):
        if len(args) == 1 and isinstance(args[0], RequestFilterAbstract):
            args = args[0].args
        if self.args[0] == 'AND':
            self.args = list(self.args) + list(args)
        else:
            self.args = and_(self.args, args)


class RequestWhere(RequestFilterAbstract):
    """ SQL 'WHERE' conditions declaration """
    pass


class RequestHaving(RequestFilterAbstract):
    """ SQL 'HAVING' conditions declaration """
    pass


class RequestOrderBy(object):
    """ SQL 'ORDER BY' operator declaration """
    def __init__(self, c, d='ASC'):
        if isinstance(c, RequestOrderBy):
            self.c = c.c
            self.d = c.d
            return
        if not isinstance(d, str) or d.lower() not in ('asc', 'desc'):
            raise TypeError("Request's ORDER BY must be set using (<Column>, [ASC|DESC]) format!")
        self.c = c
        self.d = d.upper()


class RequestGroupBy(object):
    """ SQL 'GROUP BY' operator declaration """
    def __init__(self, c, d='ASC'):
        if isinstance(c, RequestGroupBy):
            self.c = c.c
            self.d = c.d
            return
        if not isinstance(d, str) or d.lower() not in ('asc', 'desc'):
            raise TypeError("Request's GROUP BY must be set using (<Column>, [ASC|DESC]) format!")
        self.c = c
        self.d = d.upper()


class RequestLimit(object):
    """ SQL 'LIMIT' operator declaration """
    def __init__(self, *args):
        if len(args) > 2:
            raise AttributeError("Request limit must be set with (limit) or (offset, limit) syntax!")
        if not args:
            raise AttributeError("Request limit must be set with (limit) or (offset, limit) syntax!")
        if len(args) == 1:
            if not isinstance(args[0], int):
                raise TypeError("Request limit must be set using integer value(s)!")
            self.offset = None
            self.limit = args[0]
        else:
            if not isinstance(args[0], int) or not isinstance(args[1], int):
                raise TypeError("Request limit must be set using integer value(s)!")
            self.offset = args[0]
            self.limit = args[1]


class RequestTableBelongedColumn(OrmComparatorMixin, object):
    def __init__(self, k, tbl_name, c=None):
        self.k = k
        self.tbl_name = tbl_name
        self.c = c

    def __hash__(self):
        return super(OrmComparatorMixin, self).__hash__()

    def as_(self, alias):
        from .attributes.base import AttributeAliased
        return AttributeAliased(self, alias)

    def __repr__(self):
        return "TableColumn(%s.%s)" % (self.tbl_name, self.k) \
            if self.c is None \
            else "TableColumn::%s(%s.%s)" % (self.c.__class__.__name__, self.tbl_name, self.k)

    def resolve_comparator_(self, cmp, session):
        if self.c is None:
            return super(RequestTableBelongedColumn, self).resolve_comparator_(cmp, session)
        return self.c.resolve_comparator_(cmp, session)

    def make_read(self, context):
        from .attributes.columns import ColumnAttributeAbstract
        if self.c is None or not isinstance(self.c, ColumnAttributeAbstract):
            return
        self.c = self.c.make_read(context)


class RequestAliasedSource(object):
    def __init__(self, tablename, model=None):
        self.tablename = tablename
        self.model = model

    def __getattribute__(self, key):
        if key.startswith('__') and key.endswith('__'):
            return super(RequestAliasedSource, self).__getattribute__(key)
        if key in ('tablename', 'model'):
            return super(RequestAliasedSource, self).__getattribute__(key)
        c = None if self.model is None else getattr(self.model, key, None)
        return RequestTableBelongedColumn(key, self.tablename, c)


class RequestNamedColumn(OrmComparatorMixin, object):
    def __init__(self, column_name):
        self.column_name = column_name


class RequestJoinAbstract(object):
    def __init__(self, source, *args):
        self.source = source
        self.condition = list(args)
        self.join_type = "JOIN"


class RequestLeftJoin(RequestJoinAbstract):
    """ SQL 'LEFT JOIN' (or just 'JOIN') declaration """
    def __init__(self, model, *args):
        super(RequestLeftJoin, self).__init__(model, *args)
        self.join_type = 'LEFT JOIN'


class RequestRightJoin(RequestJoinAbstract):
    """ SQL 'RIGHT JOIN' declaration """
    def __init__(self, model, *args):
        super(RequestRightJoin, self).__init__(model, *args)
        self.join_type = 'RIGHT JOIN'


class RequestInnerJoin(RequestJoinAbstract):
    """ SQL 'INNER JOIN' declaration """
    def __init__(self, model, *args):
        super(RequestInnerJoin, self).__init__(model, *args)
        self.join_type = 'INNER JOIN'


class RequestFullJoin(RequestJoinAbstract):
    """ SQL 'FULL JOIN' declaration """
    def __init__(self, model, *args):
        super(RequestFullJoin, self).__init__(model, *args)
        self.join_type = 'FULL JOIN'


class DbFunctionOperator(object):
    """ A class used when needed to inform the engine about constant string operator inside a function """
    def __init__(self, text, separated=False):
        self.text = text
        self.separated = separated  # place , in front of text


class DbFunctionAbstract(OrmComparatorMixin, AttributeAbstract):
    """ Abstract class used by function declaration classes """

    def __init__(self):
        super(DbFunctionAbstract, self).__init__()
        self.l10n = False

    def __hash__(self):
        return super(OrmComparatorMixin, self).__hash__()

    def resolve(self, context, table_name=None):
        pass

    def as_(self, name):
        """ Returns this instance formatted to be named column as 'name'. """
        from .attributes.base import AttributeAliased
        return AttributeAliased(self, name)

    def text_repr(self, value, instance):
        return self._l10n_text(value)

    def _l10n_text(self, s):
        """ Tries to localize given text. """
        from .utils import gettext
        if isinstance(self.l10n, bool):
            return s if not self.l10n else gettext(s)
        return self.l10n(s) if callable(self.l10n) else s

    @staticmethod
    def _resolve_arg(arg, context, table_name=None):
        from .request import OrmRequest
        from .attributes.base import ColumnAttributeAbstract

        _params = context.params if isinstance(context, OrmRequest) else context
        if isinstance(arg, UncastableColumn):
            arg = arg.c
        elif isinstance(arg, ColumnAttributeAbstract) and context.request_type == 'select':
            arg = arg.make_read(context)
        if isinstance(arg, RawSql):
            return [str(arg.value), True]
        elif isinstance(arg, OrmRequest):
            query_ = arg.sql
            params_ = arg.params
            for k in params_:
                v = params_[k]
                k_ = 'p%i' % len(_params)
                kf_ = "%(" + k + ")s"
                kt_ = "%(" + k_ + ")s"
                query_ = query_.replace(kf_, kt_)
                _params[k_] = v
            return ["(" + query_ + ")", True]
        elif isinstance(arg, (ColumnAttributeAbstract, RequestNamedColumn)) and isinstance(context, OrmRequest):
            context.ensure_column(arg)
            return [context.sql_column(arg, alias=False, table_name=table_name), True]
        elif isinstance(arg, RequestTableBelongedColumn):
            return [context.resolve_expr(arg, allow_alias=False, table_name=table_name), True]
        elif isinstance(arg, DbFunctionAbstract):
            return [arg.resolve(context, table_name=table_name), True]
        elif isinstance(arg, DbFunctionOperator):
            return [arg.text, bool(arg.separated)]
        elif isinstance(arg, OrmComparator) and isinstance(context, OrmRequest):
            return [context.resolve_expr(arg, table_name=table_name), True]
        elif arg is None:
            return ['NULL', True]
        else:
            pn = 'p%i' % len(_params)
            an = "%(" + pn + ")s"
            _params[pn] = arg
            return [an, True]


class DbSimpleFunction(DbFunctionAbstract):
    """ NAME(arg1, arg2, arg*) """
    def __init__(self, funcname, *args, **kwargs):
        super(DbSimpleFunction, self).__init__()
        self.funcname = funcname
        self.args = args or []
        self.pre = list()
        self.post = list()
        self.modifiers = kwargs

    def resolve(self, context, table_name=None):
        """ Returns textual SQL representation of function. """
        args = []
        for arg in self.args:
            args.append(self._resolve_arg(arg, context, table_name=table_name))
        ra = ""
        if args:
            for arg in args:
                if ra and bool(arg[1]):
                    ra += ', '
                elif ra:
                    ra += ' '
                ra += str(arg[0])
        if self.modifiers:
            for arg_name in self.modifiers:
                arg_value = self.modifiers[arg_name]
                if ra:
                    ra += ' '
                ra += arg_name.upper() + ' ' + str(arg_value)
        expr_ = list()
        if self.pre:
            expr_.append(" ".join(self.pre))
        expr_.append(ra)
        if self.post:
            expr_.append(" ".join(self.post))
        return self.funcname + "(" + " ".join(expr_) + ")"


class DbCaseFunction(DbFunctionAbstract):
    """
    CASE value WHEN cases1[0] THEN cases1[1] WHEN cases2[0] THEN cases2[1] ELSE default END
    CASE WHEN cases1[0] THEN cases1[1] WHEN cases2[0] THEN cases2[1] ELSE default END
    """
    def __init__(self, has_else, value, default, *args):
        super(DbCaseFunction, self).__init__()
        self.value = value
        self.cases = args
        self.has_else = bool(has_else)
        self.default = default

    def resolve(self, context, table_name=None):
        """ Returns textual SQL representation of function. """
        csr = list()
        for cs in self.cases:
            if not isinstance(cs, (list, tuple)) or len(cs) != 2:
                raise ValueError(
                    "'case_...' functions requires that 'cases' to be set using list format"
                    " [WHEN expr, THEN expr], [WHEN expr, THEN expr]...!"
                )
            cs_when = self._resolve_arg(cs[0], context, table_name=table_name)
            cs_then = self._resolve_arg(cs[1], context, table_name=table_name)
            csv = "WHEN " + str(cs_when[0]) + " THEN " + str(cs_then[0])
            csr.append(csv)
        csr = " ".join(csr)
        if self.value is not None:
            value = self._resolve_arg(self.value, context, table_name=table_name)
            r = "CASE " + str(value[0]) + " " + csr
        else:
            r = "CASE " + csr
        if self.has_else:
            default = self._resolve_arg(self.default, context, table_name=table_name)
            r += " ELSE " + str(default[0])
        r += " END"
        return "(" + r + ")"


class DbMiddleFunction(DbFunctionAbstract):
    """ left NAME right [ex] """
    def __init__(self, name, left, right, ex=None):
        super(DbMiddleFunction, self).__init__()
        self.name = name
        self.left = left
        self.right = right
        self.ex = ex

    def resolve(self, context, table_name=None):
        """ Returns textual SQL representation of function. """
        larg_ = self._resolve_arg(self.left, context, table_name=table_name)
        rarg_ = self._resolve_arg(self.right, context, table_name=table_name)
        r = str(larg_) + " " + str(self.name) + " " + str(rarg_)
        if self.ex is not None:
            exarg_ = self._resolve_arg(self.ex, context, table_name=table_name)
            r += " " + str(exarg_)
        return r


def select_(*args, **kwargs):
    """ Helper function used to generate a SELECT request using given parameters. A shortcut
    for OrmSelectRequest's class instance creating. """
    from .request import OrmSelectRequest
    return OrmSelectRequest(*args, **kwargs)


def uncastable_(c):
    """ This function returns a wrapped uncastable column that used in functions when declaring
    _attrs which are castable itself, to prevent recursion when function resolved column which
    returns a function which resolves an argument which is castable column again and again
    and again. """
    return UncastableColumn(c)


def raw_(sql):
    """ Used to inform the engine that this is a textual name of the requesting column
    or other textual raw query """
    return RawSql(sql)


def left_join_(cls, *args):
    """ Returns LEFT JOIN instance """
    return RequestLeftJoin(cls, *args)


def join_(cls, *args):
    """ Returns LEFT JOIN instance """
    return left_join_(cls, *args)


def right_join_(cls, *args):
    """ Returns RIGHT JOIN instance """
    return RequestRightJoin(cls, *args)


def inner_join_(cls, *args):
    """ Returns INNER JOIN instance """
    return RequestInnerJoin(cls, *args)


def full_join_(cls, *args):
    """ Returns FULL JOIN instance """
    return RequestFullJoin(cls, *args)


def t_(table, model=None):
    """ Offers a source by name of table alias. """
    from .models.base import OrmModelAliased
    if isinstance(table, OrmModelAliased):
        table_name = table.alias
        model = model if model is not None else table.model
    else:
        table_name = table
    return RequestAliasedSource(table_name, model)


def c_(column_name):
    """ Offers a column by name of column alias. """
    return RequestNamedColumn(column_name)


def and_(*args):
    """ SQL 'AND' operator """
    return ['AND'] + list(args)


def or_(*args):
    """ SQL 'OR' operator """
    return ['OR'] + list(args)


def not_(expr):
    """ SQL 'NOT' operator """
    return func_('NOT', expr)


def filter_(*args):
    """ Is synonym to 'where_' function """
    return RequestWhere(*args)


def where_(*args):
    """ Defines an SQL 'WHERE' condition expression """
    return RequestWhere(*args)


def having_(*args):
    """ Defines an SQL 'HAVING' condition expression """
    return RequestHaving(*args)


def limit_(*args):
    """ Defines SQL 'LIMIT' operator """
    return RequestLimit(*args)


def order_by_(c, d='ASC'):
    """ Defines SQL 'ORDER BY' operator """
    return RequestOrderBy(c, d)


def group_by_(c):
    """ Defines SQL 'GROUP BY' operator """
    return RequestGroupBy(c)


def textual_(c):
    """ Resolves the column into textual representation if 'options' parameter of the
    attribute is set. """
    options = getattr(c, 'options', None)
    if not options:
        return concat_(c, '')
    if not isinstance(options, dict):
        raise OrmDefinitionError("attribute's 'options' must be a (dict) type!")
    exprs = list()
    for k in options:
        v = options[k]
        exprs.append([k, v])
    return case_else_(c, concat_(c, ''), *exprs)


def func_(name, *args, **kwargs):
    """ General (any custom) SQL function declaration """
    if not isinstance(name, str):
        raise ValueError("'func_' require that 'name' must be a string!")
    name = name.upper()
    return DbSimpleFunction(name, *args, **kwargs)


def isnull_(expr):
    """ ISNULL(expr) """
    return func_('ISNULL', expr)


def exists_(expr):
    """ EXISTS(expr) """
    return func_('EXISTS', expr)


def case_(value, *args):
    """ CASE value WHEN a1 THEN b1 WHEN a2 THEN b2 END """
    return DbCaseFunction(False, value, None, *args)


def case_else_(value, default, *args):
    """ CASE value WHEN a1 THEN b1 WHEN a2 THEN b2 ELSE default END """
    return DbCaseFunction(True, value, default, *args)


def case_when_(*args):
    """ CASE WHEN a1 THEN b1 WHEN a2 THEN b2 END """
    return case_(None, *args)


def case_when_else_(default, *args):
    """ CASE WHEN a1 THEN b1 WHEN a2 THEN b2 ELSE default END """
    return case_else_(None, default, *args)


def if_(expr1, expr2, expr3):
    """ IF(expr1, expr2, expr3) """
    return func_('IF', expr1, expr2, expr3)


def ifnull_(expr1, expr2):
    """ IFNULL(expr1, expr2) """
    return func_('IFNULL', expr1, expr2)


def nullif_(expr1, expr2):
    """ NULLIF(expr1, expr2) """
    return func_('NULLIF', expr1, expr2)


def abs_(x):
    """ ABS(x) """
    return func_('ABC', x)


def asin_(x):
    """ ASIN(x) """
    return func_('ASIN', x)


def atan_(x):
    """ ATAN(x) """
    return func_('ATAN', x)


def atan2_(y, x):
    """ ATAN2(y, x) """
    return func_('ATAN2', y, x)


def ceiling_(x):
    """ CEILING(x) """
    return func_('CEILING', x)


def ceil_(x):
    """ Alias for 'ceiling' """
    return ceiling_(x)


def conv_(n, from_base, to_base):
    """ CONV(n, from_base, to_base) """
    return func_('CONV', n, from_base, to_base)


def cos_(x):
    """ COS(x) """
    return func_('COS', x)


def cot_(x):
    """ COT(x) """
    return func_('COT', x)


def crc32_(expr):
    """ CRC32(expr) """
    return func_('CRC32', expr)


def degrees_(x):
    """ DEGREES(x) """
    return func_('DEGREES', x)


def exp_(x):
    """ EXP(x) """
    return func_('EXP', x)


def floor_(x):
    """ FLOOR(x) """
    return func_('FLOOR', x)


def format_(x, d, locale=None):
    """
    FORMAT(x, d)
    FORMAT(x, d, locale)
    """
    return func_('FORMAT', x, d) if locale is None else func_('FORMAT', x, d, locale)


def hex_(n):
    """ HEX(n) """
    return func_('HEX', n)


def ln_(x):
    """ LN(x) """
    return func_('LN', x)


def log_(x, y=None):
    """
    LOG(x)
    LOG(x, y)
    """
    return func_('LOG', x) if y is None else func_('LOG', x, y)


def log2_(x):
    """ LOG2(x) """
    return func_('LOG2', x)


def log10_(x):
    """ LOG10(x) """
    return func_('LOG10', x)


def mod_(n, m):
    """ MOD(n, m) """
    return func_('MOD', n, m)


def pi_():
    """ PI() """
    return func_('PI')


def pow_(x, y):
    """ POW(x, y) """
    return func_('POW', x, y)


def power_(x, y):
    """ Alias for 'pow' """
    return pow_(x, y)


def radians_(x):
    """ RADIANS(x) """
    return func_('RADIANS', x)


def rand_(n=None):
    """
    RAND()
    RAND(n)
    """
    return func_('RAND') if n is None else func_('RAND', n)


def round_(x, d=None):
    """
    ROUND(x)
    ROUND(x, d)
    """
    return func_('ROUND', x) if d is None else func_('ROUND', x, d)


def sign_(x):
    """ SIGN(x) """
    return func_('SIGN', x)


def sin_(x):
    """ SIN(x) """
    return func_('SIN', x)


def sqrt_(x):
    """ SQRT(x) """
    return func_('SQRT', x)


def tan_(x):
    """ TAN(x) """
    return func_('TAN', x)


def truncate_(x, d):
    """ TRUNCATE(x, d) """
    return func_('TRUNCATE', x, d)


def ascii_(s):
    """ ASCII(s) """
    return func_('ASCII', s)


def bin_(n):
    """ BIN(n) """
    return func_('BIN', n)


def bin_length_(s):
    """ BIN_LENGTH(s) """
    return func_('BIN_LENGTH', s)


def char_(*args, **kwargs):
    """
    CHAR(arg1, arg2, ...)
    CHAR(arg1, arg2, ... USING using)
    """
    kw = {}
    if 'using' in kwargs:
        kw['USING'] = kwargs.pop('using')
    return func_('CHAR', *args, **kw)


def char_length_(s):
    """ CHAR_LENGTH(s) """
    return func_('CHAR_LENGTH', s)


def character_length_(s):
    """ Alias for 'char_length' """
    return char_length_(s)


def concat_(*args):
    """ CONCAT(arg1, arg2, ...) """
    return func_('CONCAT', *args)


def concat_ws_(separator, *args):
    """ CONCAT_WS(separator, arg1, arg2, ...) """
    return func_('CONCAT_WS', separator, *args)


def elt_(n, *args):
    """ ELT(n, arg1, arg2, ...) """
    return func_('ELT', n, *args)


def export_set_(bits, on, off, separator=None, number_of_bits=None):
    """
    EXPORT_SET(bits, on, off)
    EXPORT_SET(bits, on, off, separator)
    EXPORT_SET(bits, on, off, separator, number_of_bits)
    """
    if number_of_bits is not None:
        return func_("EXPORT_SET", bits, on, off, separator, number_of_bits)
    elif separator is not None:
        return func_("EXPORT_SET", bits, on, off, separator)
    else:
        return func_("EXPORT_SET", bits, on, off)


def field_(s, *args):
    """ FIELD(s, arg1, arg2, ...) """
    return func_('FIELD', s, *args)


def find_in_set_(s, l):
    """ FIND_IN_SET(s, l) """
    return func_('FIND_IN_SET', s, l)


def from_base64_(s):
    """ FROM_BASE64(s) """
    return func_('FROM_BASE64', s)


def insert_(s, pos, length, newstr):
    """ INSERT(s, pos, length, newstr) """
    return func_('INSERT', s, pos, length, newstr)


def instr_(s, substr):
    """ INSTR(s, substr) """
    return func_("INSTR", s, substr)


def lower_(s):
    """ LOWER(s) """
    return func_('LOWER', s)


def lcase_(s):
    """ Alias for 'lower' """
    return lower_(s)


def left_(s, length):
    """ LEFT(s, length) """
    return func_('LEFT', s, length)


def length_(s):
    """ LENGTH(s) """
    return func_('LENGTH', s)


def locate_(substr, s, pos=None):
    """
    LOCATE(substr, s)
    LOCATE(substr, s, pos)
    """
    return func_('LOCATE', substr, s) if pos is None else func_('LOCATE', substr, s, pos)


def lpad_(s, length, padstr):
    """ LPAD(s, length, padstr) """
    return func_('LPAD', s, length, padstr)


def ltrim_(s):
    """ LTRIM(s) """
    return func_('LTRIM', s)


def make_set(bits, *args):
    """ MAKE_SET(bits, arg1, arg2, ...) """
    return func_('MAKE_SET', bits, *args)


def mid_(s, pos, length):
    """ MID(s, pos, length) """
    return substring_(s, pos, length)


def oct_(n):
    """ OCT(n) """
    return func_('OCT', n)


def octet_length(s):
    """ OCTET_LENGTH(s) """
    return length_(s)


def ord_(s):
    """ ORD(s) """
    return func_('ORD', s)


def position_(substr, s):
    """ Alias for 'locate' """
    return locate_(substr, s)


def quote_(s):
    """ QUOTE(s) """
    return func_('QUOTE', s)


def repeat(s, cnt):
    """ REPEAT(s, cnt) """
    return func_('REPEAT', s, cnt)


def replace_(s, from_str, to_str):
    """ REPLACE(s, from_str, to_str) """
    return func_('REPLACE', s, from_str, to_str)


def reverse_(s):
    """ REVERSE(s) """
    return func_('REVERSE', s)


def right_(s, length):
    """ RIGHT(s, length) """
    return func_('RIGHT', s, length)


def rpad_(s, length, padstr):
    """ RPAD(s, length, padstr) """
    return func_('RPAD', s, length, padstr)


def rtrim_(s):
    """ RTRIM(s) """
    return func_('RTRIM', s)


def soundex(s):
    """ SOUNDEX(s) """
    return func_('SOUNDEX', s)


def space_(n):
    """ SPACE(n) """
    return func_('SPACE', n)


def substr_(s, pos, length=None):
    """ Alias for 'substring' """
    return substring_(s, pos, length)


def substring_(s, pos, length=None):
    """
    SUBSTRING(s, pos)
    SUBSTRING(s, pos, length)
    """
    return func_('SUBSTRING', s, pos) if length is None else func_('SUBSTRING', s, pos, length)


def substring_index_(s, delim, count):
    """ SUBSTRING_INDEX(s, delimn, count) """
    return func_('SUBSTRING_INDEX', s, delim, count)


def to_base64_(s):
    """ TO_BASE64(s) """
    return func_('TO_BASE64', s)


def trim_(s, from_=None):
    """
    TRIM(s)
    TRIM(from_ FROM s)
    """
    return func_('TRIM', s) if from_ is None else func_('TRIM', from_, DbFunctionOperator('FROM'), s)


def trim_leading_(s, from_=None):
    """
    TRIM(LEADING s)
    TRIM(LEADING from_ FROM s)
    """
    if from_ is None:
        return func_('TRIM', DbFunctionOperator('LEADING'), s)
    else:
        return func_('TRIM', DbFunctionOperator('LEADING'), from_, DbFunctionOperator('FROM'), s)


def trim_trailing_(s, from_=None):
    """
    TRIM(TRAILING s)
    TRIM(TRAILING from_ FROM s)
    """
    if from_ is None:
        return func_('TRIM', DbFunctionOperator('TRAILING'), s)
    else:
        return func_('TRIM', DbFunctionOperator('TRAILING'), from_, DbFunctionOperator('FROM'), s)


def trim_both_(s, from_=None):
    """
    TRIM(BOTH s)
    TRIM(BOTH from_ FROM s)
    """
    if from_ is None:
        return func_('TRIM', DbFunctionOperator('BOTH'), s)
    else:
        return func_('TRIM', DbFunctionOperator('BOTH'), from_, DbFunctionOperator('FROM'), s)


def ucase_(s):
    """ Alias for 'upper' """
    return upper_(s)


def unhex_(s):
    """ UNHEX(s) """
    return func_('UNHEX', s)


def upper_(s):
    """ UPPER(s) """
    return func_('UPPER', s)


def strcmp_(s1, s2, collate=None):
    """
    STRCMP(s1, s2)
    STRCMP(s1, s2 COLLATE collate)
    """
    if collate is None:
        return func_('STRCMP', s1, s2)
    else:
        return func_('STRCMP', s1, s2, collate=collate)


def like_(expr, pat):
    """ expr LIKE pat """
    return DbMiddleFunction('LIKE', expr, pat)


def notlike_(expr, pat):
    """ expr NOT LINKE pat """
    return DbMiddleFunction('NOT LIKE', expr, pat)


def rlike_(expr, pat):
    """ expr RLIKE pat """
    return DbMiddleFunction('RLIKE', expr, pat)


def not_rlike_(expr, pat):
    """ expr NOT RLIKE pat """
    return DbMiddleFunction('NOT RLIKE', expr, pat)


def regexp_(expr, pat):
    """ expr REGEXP pat """
    return DbMiddleFunction('REGEXP', expr, pat)


def not_regexp_(expr, pat):
    """ expr NOT REGEXP pat """
    return DbMiddleFunction('NOT REGEXP', expr, pat)


def adddate_(d, interval=None, days=None):
    """
    ADDDATE(d, INTERVAL interval DAYS)
    ADDDATE(d, days)
    """
    if interval is None and days is None:
        raise AttributeError("'ADDDATE' required 'interval' or 'days' to be set!")
    if interval:
        interval_ = "INTERVAL " + interval
        return func_('ADDDATE', d, DbFunctionOperator(interval_, True))
    else:
        return func_('ADDDATE', d, days)


def addtime_(expr1, expr2):
    """ ADDTIME(expr1, expr2) """
    return func_('ADDTIME', expr1, expr2)


def convert_tz_(dt, from_tz, to_tz):
    """ CONVERT_TZ(dt, from_tz, to_tz) """
    return func_('CONVERT_TZ', dt, from_tz, to_tz)


def curdate_():
    """ CURDATE() """
    return func_('CURDATE')


def current_date():
    """ Alias for 'curdate' """
    return curdate_()


def current_time(fsp=None):
    """ Alias for 'curtime' """
    return curtime_(fsp)


def curtime_(fsp=None):
    """
    CURTIME()
    CURTIME(fsp)
    """
    return func_('CURTIME') if fsp is None else func_('CURTIME', fsp)


def date_(expr):
    """ DATE(expr) """
    return func_('DATE', expr)


def datediff_(expr1, expr2):
    """ DATEDIFF(expr1, expr2) """
    return func_('DATEDIFF', expr1, expr2)


def date_add_(d, interval):
    """ DATE_ADD(d INTERVAL interval) """
    return adddate_(d, interval=interval)


def date_sub_(d, interval):
    """ DATE_SUB(d INTERVAL interval) """
    return subdate_(d, interval=interval)


def date_format_(d, fmt):
    """ DATE_FORMAT(d, fmt) """
    return func_('DATE_FORMAT', d, fmt)


def subdate_(d, interval=None, days=None):
    """
    SUBDATE(d, INTERVAL interval)
    SUBDATE(d, days)
    """
    if interval is None and days is None:
        raise AttributeError("'SUBDATE' required 'interval' or 'days' to be set!")
    if interval:
        interval_ = "INTERVAL " + interval
        return func_('SUBDATE', d, DbFunctionOperator(interval_, True))
    else:
        return func_('SUBDATE', d, days)


def dayofmonth_(d):
    """ DAYOFMONTH(d) """
    return func_('DAYOFMONTH', d)


def day_(d):
    """ DAY(d) """
    return dayofmonth_(d)


def dayname_(d):
    """ DAYNAME(d) """
    return func_('DAYNAME', d)


def dayofweek_(d):
    """ DAYOFWEEK(d) """
    return func_('DAYOFWEEK', d)


def dayofyear_(d):
    """ DAYOFYEAR(d) """
    return func_('DAYOFYEAR', d)


def extract_(unit, d):
    """ EXTRACT(unit FROM d) """
    return func_('EXTRACT', unit, DbFunctionOperator('FROM'), d)


def from_days_(n):
    """ FROM_DAYS(n) """
    return func_('FROM_DAYS', n)


def from_unixtime_(unix_timestamp, fmt=None):
    """
    FROM_UNIXTIME(unix_timestamp)
    FROM_UNIXTIME(unix_timestamp, fmt)
    """
    return func_('FROM_UNIXTIME', unix_timestamp) if fmt is None \
        else func_('FROM_UNIXTIME', unix_timestamp, fmt)


def get_format_(type_, target_):
    """ GET_FORMAT(type_, target_) """
    if not isinstance(type_, str):
        raise AttributeError("'GET_FORMAT'('type_') has to be string!")
    if not isinstance(target_, str):
        raise AttributeError("'GET_FORMAT'('target_') has to be a string!")
    type_ = type_.upper()
    target_ = target_.upper()
    if type_ not in ('DATE', 'TIME', 'DATETIME'):
        raise ValueError("'GET_FORMAT'('type_') must be 'DATE', 'TIME' or 'DATETIME'!")
    if target_ not in ('EUR', 'USA', 'JIS', 'ISO', 'INTERNAL'):
        raise ValueError("'GET_FORMAT'('target_') must be 'EUR', 'USA', 'JIS', 'ISO' or 'INTERNAL'!")
    return func_('GET_FORMAT', type_, target_)


def hour_(t):
    """ HOUR(t) """
    return func_('HOUR', t)


def last_day_(d):
    """ LAST_DAY(d) """
    return func_('LAST_DAY', d)


def localtime_(fsp=None):
    """
    LOCALTIME()
    LOCALTIME(fsp)
    """
    return now_(fsp)


def localtimestamp_(fsp=None):
    """
    LOCALTIMESTAMP()
    LOCALTIMESTAMP(fsp)
    """
    return now_(fsp)


def makedate_(year, dayofyear):
    """ MAKEDATE(year, dayofyear) """
    return func_('MAKEDATE', year, dayofyear)


def maketime_(hour, minute, second):
    """ MAKETIME(hour, minute, second) """
    return func_('MAKETIME', hour, minute, second)


def microsecond_(expr):
    """ MICROSECOND(expr) """
    return func_('MICROSECOND', expr)


def minute_(t):
    """ MINUTE(t) """
    return func_('MINTE', t)


def month_(d):
    """ MONTH(d) """
    return func_('MONTH', d)


def monthname_(d):
    """ MONTHNAME(d) """
    return func_('MONTHDATE', d)


def now_(fsp=None):
    """
    NOW()
    NOW(fsp)
    """
    return func_('NOW') if fsp is None else func_('NOW', fsp)


def period_add_(p, n):
    """ PERIOD_ADD(p, n) """
    return func_('PERIOD_ADD', p, n)


def period_diff_(p1, p2):
    """ PERIOD_DIFF(p1, p2) """
    return func_('PERIOD_DEFF', p1, p2)


def quarter_(d):
    """ QUARTER(d) """
    return func_('QUARTER', d)


def second_(t):
    """ SECOND(t) """
    return func_('SECOND', t)


def sec_to_time_(seconds):
    """ SEC_TO_TIME(second) """
    return func_('SEC_TO_TIME', seconds)


def str_to_date_(s, fmt):
    """ STR_TO_DATE(s, fmt) """
    return func_('STR_TO_DATE', s, fmt)


def subtime_(expr1, expr2):
    """ SUBTIME(expr1, expr2) """
    return func_('SUBTIME', expr1, expr2)


def sysdate_(fsp=None):
    """
    SYSDATE()
    SYSDATE(fsp)
    """
    return func_('SYSDATE') if fsp is None else func_('SYSDATE', fsp)


def time_(expr):
    """ TIME(expr) """
    return func_('TIME', expr)


def timediff_(expr1, expr2):
    """ TIMEDIFF(expr1, expr2) """
    return func_('TIMEDIFF', expr1, expr2)


def timestamp_(expr, expr2=None):
    """
    TIMESTAMP(expr)
    TIMESTAMP(expr, expr2)
    """
    return func_('TIMESTAMP', expr) if expr2 is None else func_('TIMESTAMP', expr, expr2)


def timestampadd_(unit, interval, datetime_expr):
    """ TIMESTAMPADD(unit, interval, datetime_expr) """
    return func_('TIMESTAMPADD', DbFunctionOperator(unit), interval, datetime_expr)


def timestampdiff_(unit, datetime_expr1, datetime_expr2):
    """ TIMESTAMPDIFF(unit, datetime_expr1, datetime_expr2) """
    return func_('TIMESTAMPDIFF', DbFunctionOperator(unit), datetime_expr1, datetime_expr2)


def time_format_(t, fmt):
    """ TIME_FORMAT(t, fmt) """
    return func_('TIME_FORMAT', t, fmt)


def time_to_sec_(t):
    """ TIME_TO_SEC(t) """
    return func_('TIME_TO_SEC', t)


def to_days_(d):
    """ TO_DAYS(d) """
    return func_('TO_DAYS', d)


def to_seconds_(expr):
    """ TO_SECONDS(expr) """
    return func_('TO_SECONDS', expr)


def unix_timestamp_(d=None):
    """
    UNIX_TIMESTAMP()
    UNIX_TIMESTAMP(d)
    """
    return func_('UNIX_TIMESTAMP') if d is None else func_('UNIX_TIMESTAMP', d)


def utc_date_():
    """ UTC_DATE() """
    return func_('UTC_DATE')


def utc_time_(fsp=None):
    """
    UTC_TIME()
    UTC_TIME(fsp)
    """
    return func_('UTC_TIME') if fsp is None else func_('UTC_TIME', fsp)


def utc_timestamp_(fsp=None):
    """
    UTC_TIMESTAMP()
    UTC_TIMESTAMP(fsp)
    """
    return func_('UTC_TIMESTAMP') if fsp is None else func_('UTC_TIMESTAMP', fsp)


def week_(d, mode=None):
    """
    WEEK(d)
    WEEK(d, mode)
    """
    return func_('WEEK', d) if mode is None else func_('WEEK', d, mode)


def weekday_(d):
    """ WEEKDAY(d) """
    return func_('WEEKDAY', d)


def weekofyear_(d):
    """ WEEKOFYEAR(d) """
    return func_('WEEKOFYEAR', d)


def year_(d):
    """ YEAR(d) """
    return func_('YEAR', d)


def yearweek_(d, mode=None):
    """
    YEARWEEK(d)
    YEARWEEK(d, mode)
    """
    return func_('YEARWEEK', d) if mode is None else func_('YEARWEEK', d, mode)


def cast_(expr, type_):
    """ CAST(expr AS type_) """
    if not isinstance(type_, str):
        raise ValueError("'CAST'('type_') must be a string!")
    _as = 'AS ' + str(type_)
    return func_('CAST', expr, DbFunctionOperator(_as))


def convert_(expr, type_):
    """ CONVERT(expr, type_) """
    if not isinstance(type_, str):
        raise ValueError("'CONVERT'('type_') must be a string!")
    return func_('CONVERT', expr, type_)


def convert_using_(expr, using):
    """ CONVERT(expr USING using) """
    if not isinstance(using, str):
        raise ValueError("'CONVERT'('using') must be a string!")
    return func_('CONVERT', expr, DbFunctionOperator('USING ' + str(using)))


def binary_(expr):
    """ CAST(expr AS BINARY) """
    return cast_(expr, 'BINARY')


def extractvalue_(xml_frag, xpath_expr):
    """ ExtractValue(xml_frag, xpath_expr) """
    return func_("ExtractValue", xml_frag, xpath_expr)


def updatexml_(xml_target, xpath_expr, new_xml):
    """ UpdateXML(xml_target, xpath_expr, new_xml) """
    return func_("UpdateXML", xml_target, xpath_expr, new_xml)


def bit_count_(n):
    """ BIT_COUNT(n) """
    return func_('BIT_COUNT', n)


def aes_decrypt_(crypt_str, key_str, init_vector=None):
    """
    AES_DECRYPT(crypt_str, key_str)
    AES_DECRYPT(crypt_str, key_str, init_vector)
    """
    return func_('AES_DECRYPT', crypt_str, key_str) if init_vector is None \
        else func_('AES_DECRYPT', crypt_str, key_str, init_vector)


def aes_encrypt_(s, key_str, init_vector=None):
    """
    AES_ENCRYPT(crypt_str, key_str)
    AES_ENCRYPT(crypt_str, key_str, init_vector)
    """
    return func_('AES_ENCRYPT', s, key_str) if init_vector is None \
        else func_('AES_ENCRYPT', s, key_str, init_vector)


def compress_(s):
    """ COMPRESS(s) """
    return func_('COMPRESS', s)


def md5_(s):
    """ MD5(s) """
    return func_('MD5', s)


def random_bytes_(length):
    """ RANDOM_BYTES(length) """
    return func_('RANDOM_BYTES', length)


def sha_(s):
    """ SHA(s) """
    return func_('SHA', s)


def sha1_(s):
    """ Alias for 'sha' """
    return sha_(s)


def sha2_(s, hash_length):
    """ SHA2(s, hash_length) """
    return func_('SHA2', s, hash_length)


def uncompress_(s):
    """ UNCOMPRESS(s) """
    return func_('UNCOMPRESS', s)


def uncompressed_length_(compressed_string):
    """ UNCOMPRESSES_LENGTH(compressed_string) """
    return func_('UNCOMPRESSED_LENGTH', compressed_string)


def validate_password_strength(s):
    """ VALiDATE_PASSWORD_STRENGTH(s) """
    return func_('VALIDATE_PASSWORD_STRENGTH', s)


def any_value_(arg):
    """ ANY_VALUE(arg) """
    return func_('ANY_VALUE', arg)


def default_(col_name):
    """ DEFAULT(col_name) """
    return func_('DEFAULT', col_name)


def inet_aton_(expr):
    """ INET_ATON(expr) """
    return func_('INET_ATON', expr)


def inet_ntoa_(expr):
    """ INET_NTOA(expr) """
    return func_('INET_NTOA', expr)


def inet6_aton_(expr):
    """ INET6_ATON(expr) """
    return func_('INET6_ATON', expr)


def inet6_ntoa_(expr):
    """ INET6_NTOA(expr) """
    return func_('INET6_NTOA', expr)


def is_ipv4_(expr):
    """ IS_IPV4(expr) """
    return func_('IS_IPV4', expr)


def is_ipv4_compat_(expr):
    """ IS_IPV4_COMPAT(expr) """
    return func_('IS_IPV4_COMPAT', expr)


def is_ipv4_mapped_(expr):
    """ IS_IPV4_MAPPED(expr) """
    return func_('IS_IPV4_MAPPED', expr)


def is_ipv6_(expr):
    """ IS_IPV6(expr) """
    return func_('IS_IPV6', expr)


def uuid_():
    """ UUID() """
    return func_('UUID')


def uuid_short_():
    """ UUID_SHORT() """
    return func_('UUID_SHORT')


def avg_(expr, distinct=False):
    """
    AVG(expr)
    AVG(DISTINCT expr)
    """
    return func_('AVG', expr) if not distinct \
        else func_('AVG', DbFunctionOperator('DISTINCT'), expr)


def bit_and_(expr):
    """ BIT_AND(expr) """
    return func_('BIT_AND', expr)


def bit_or_(expr):
    """ BIT_OR(expr) """
    return func_('BIT_OR', expr)


def bit_xor_(expr):
    """ BIT_XOR(expr) """
    return func_('BIT_XOR', expr)


def count_(expr):
    """ COUNT(expr) """
    return func_('COUNT', expr)


def count_distinct_(*args):
    """ COUNT(DISTINCT arg1, arg2, ...) """
    return func_('COUNT', DbFunctionOperator('DISTINCT'), *args)


def max_(expr, distinct=False):
    """
    MAX(expr)
    MAX(DISTINCT expr)
    """
    return func_('MAX', expr) if not distinct \
        else func_('MAX', DbFunctionOperator('DISTINCT'), expr)


def min_(expr, distinct=False):
    """
    MIN(expr)
    MIN(DISTINCT expr)
    """
    return func_('MIN', expr) if not distinct \
        else func_('MIN', DbFunctionOperator('DISTINCT'), expr)


def std_(expr):
    """ STD(expr) """
    return func_('STD', expr)


def stddev_(expr):
    """ STDDEV(expr) """
    return func_('STDDEV', expr)


def stddev_pop_(expr):
    """ STDDEV_POP(expr) """
    return func_('STDDEV_POP', expr)


def stddev_samp_(expr):
    """ STDDEV_SAMP(expr) """
    return func_('STDDEV_SAMP', expr)


def sum_(expr, distinct=False):
    """
    SUM(expr)
    SUM(DISTINCT expr)
    """
    return func_('SUM', expr) if not distinct \
        else func_('SUM', DbFunctionOperator('DISTINCT'), expr)


def var_pop_(expr):
    """ VAR_POP(expr) """
    return func_('VAR_POP', expr)


def var_samp_(expr):
    """ VAR_SAMP(expr) """
    return func_('VAR_SAMP', expr)


def variance_(expr):
    """ VARIANCE(expr) """
    return func_('VARIANCE', expr)


def host_(expr):
    """ PostgreSQL only: HOST(expr) """
    return func_('HOST', expr)


def pg_text_(expr):
    """ PostgresSQL only: TEXT(expr) """
    return func_('TEXT', expr)

