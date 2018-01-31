import copy
import inspect
from pc23 import xrange
from ..mapper import mapper
from ..utils import gettext
from ..exceptions import OrmParameterError, OrmInvalidKey, OrmValueVerificationError, OrmAttributeTypeMistake, \
    OrmComparatorValueError
from ..values import AttributeValueNull


FK_ONDELETE_CASCADE = 'CASCADE'
FK_ONDELETE_SET_NULL = 'SET NULL'
FK_ONDELETE_RESTRICT = 'RESTRICT'
FK_ONDELETE_ON_ACTION = 'RESTRICT'
FK_ONUPDATE_CASCADE = 'CASCADE'
FK_ONUPDATE_SET_NULL = 'SET NULL'
FK_ONUPDATE_RESTRICT = 'RESTRICT'
FK_ONUPDATE_ON_ACTION = 'RESTRICT'


class OrmComparatorMixin(object):
    """ Abstract comparator class which may be inherited by other classes to
    give ORM condition processing, like equals to, greater than and etc. """
    def __eq__(self, other):
        return OrmComparator(self, '=', other)

    def __ne__(self, other):
        return OrmComparator(self, '!=', other)

    def __gt__(self, other):
        return OrmComparator(self, '>', other)

    def __lt__(self, other):
        return OrmComparator(self, '<', other)

    def __ge__(self, other):
        return OrmComparator(self, '>=', other)

    def __le__(self, other):
        return OrmComparator(self, '<=', other)

    def __invert__(self):
        return OrmComparator(self, '~')

    def __lshift__(self, other):
        return OrmComparator(self, '<<', other)

    def __rshift__(self, other):
        return OrmComparator(self, '>>', other)

    def __and__(self, other):
        return OrmComparator(self, '&', other)

    def __or__(self, other):
        return OrmComparator(self, '|', other)

    def __xor__(self, other):
        return OrmComparator(self, '^', other)

    def is_(self, other):
        if other is None:
            return OrmComparator(self, 'ISNULL')
        return self.__eq__(other)

    def isnot_(self, other):
        if other is None:
            return OrmComparator(self, '!ISNULL')
        return self.__ne__(other)

    @property
    def isnull_(self):
        return OrmComparator(self, 'ISNULL')

    @property
    def notnull_(self):
        return OrmComparator(self, '!ISNULL')

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
        return OrmComparator(self, 'TRUE')

    @property
    def false_(self):
        return OrmComparator(self, 'FALSE')

    def in_(self, *args):
        if len(args) == 0:
            raise OrmParameterError("Column.in_() requires at least one value to be given!")
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = list(args[0])
        return OrmComparator(self, 'IN', args)

    def notin_(self, *args):
        if len(args) == 0:
            raise OrmParameterError("Column.in_() requires at least one value to be given!")
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = list(args[0])
        return OrmComparator(self, '!IN', args)

    def like_(self, value):
        return OrmComparator(self, 'LIKE', value)

    def notlike_(self, value):
        return OrmComparator(self, '!LIKE', value)

    def contains_(self, value):
        return self.__eq__(value)

    def not_contains_(self, value):
        return self.__ne__(value)

    def find_(self, value):
        from ..funcs import lower_, textual_
        if not isinstance(value, str):
            if value is None:
                raise OrmComparatorValueError("cannot search for NULL value using 'find_' comparator!")
            value = str(value)
        return OrmComparator(lower_(textual_(self)), 'LIKE', "%%%s%%" % value.lower()) \
            if not self.strict_find \
            else OrmComparator(lower_(textual_(self)), '=', value.lower())

    def resolve_comparator_(self, cmp, session):
        return cmp

    def corresponds_to_(self, value):
        return OrmComparator(self.resolve_opts_to_case(), '=', value)

    def isas_(self, value):
        return self.corresponds_to_(value)


class OrmComparator(object):
    """ A class, used for specific filter (where, having,...) to be declared """
    def __init__(self, item, cmp, value=None):
        self.cmp = cmp
        self.item = item
        self.value = value

    def resolve(self, session):
        return self.item.resolve_comparator_(self, session)


class AttributeAbstract(object):
    """ An abstract class for all declared as data types and relationships attributes
    in the model. """
    declaration_order = 10

    def __new__(cls, *args, **kwargs):
        instance = super(AttributeAbstract, cls).__new__(cls)
        instance.declaration_order = AttributeAbstract.declaration_order
        instance.template_model = None
        instance.template_k = None
        AttributeAbstract.declaration_order += 10
        return instance

    def __init__(self):
        self._validated = True
        self.auto_created = False
        self.model = None
        self.tbl_k = None
        self.model_k = None
        self.base_type = None
        self.parent_model_k = None
        self.parent_tbl_k = None
        self.parent_model = None
        self.belongs_to_template = False
        self.template_model = None
        self.template_k = None
        self.on_new = None
        self.on_change = None
        self.setter = None
        self.getter = None
        self.foreign_key = None
        self.triggers = list()

    def __repr__(self):
        if self.model is not None:
            return "%s(%s.%s)" % (self.__class__.__name__, self.model.__name__, self.model_k)
        else:
            return str(self.__class__.__name__)

    def _attr_from_template(self, inst_value):
        from ..models.base import OrmModel
        if inspect.isclass(inst_value) and issubclass(inst_value, OrmModel) and inst_value == self.template_model:
            # Reassigning attribute's property pointing to the template itself - to the
            # end model itself.
            inst_value = self.model
            return inst_value
        if isinstance(inst_value, AttributeAbstract) and inst_value.belongs_to_template:
            # Reassigning a pointer to the attribute of the template to the corresponding
            # attribute of end Model.
            inst_value = getattr(self.model, inst_value.model_k, None)
            return inst_value
        if isinstance(inst_value, dict):
            for k, v in dict(inst_value).items():
                inst_value[k] = self._attr_from_template(v)
            return inst_value
        if isinstance(inst_value, list):
            for i in xrange(len(inst_value)):
                inst_value[i] = self._attr_from_template(inst_value[i])
            return inst_value
        if isinstance(inst_value, tuple):
            l_ = list()
            for i in inst_value:
                l_.append(self._attr_from_template(i))
            return tuple(l_)
        return inst_value

    def from_template(self):
        keys = dir(self)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            cls_attr = getattr(self.__class__, k, None)
            if type(cls_attr) in (property, bool, int, float, str) \
                    or hasattr(cls_attr, '__call__') \
                    or callable(cls_attr):
                continue
            inst_value = getattr(self, k)
            if inst_value is None or type(inst_value) in (bool, int, float, str):
                continue
            setattr(self, k, self._attr_from_template(inst_value))

    def get_instance_value(self, instance):
        return instance.__getattribute__(self.model_k)

    @classmethod
    def get_next_declaration_order(cls):
        r = cls.declaration_order
        cls.declaration_order += 10
        return r

    def _get_f_value(self, p_name, default=None):
        v = getattr(self, p_name)
        if v is None:
            return default
        if callable(v):
            return v()
        return v

    def on_declare(self):
        pass

    def on_model_declared(self):
        pass

    def validate(self):
        pass

    def initialize(self, instance, k):
        pass

    def register_trigger(self):
        pass

    def call_on_change(self, instance, key, value):
        if self.on_change is not None:
            if not callable(self.on_change):
                raise OrmAttributeTypeMistake(
                    "attribute's `on_change` must be a callable function with at least three arguments:"
                    " (instance, key, value)!"
                )
            self.on_change(instance, key, value)
        if self.triggers:
            for t in self.triggers:
                t(self, instance, key, value)

    def on_instance_load(self, instance):
        pass


class DataAttributeAbstract(AttributeAbstract):
    """ The type of model's attribute which is able to store some value itself (directly
    by holding a kind of value, or virtually) """
    def __init__(self, **kwargs):
        super(DataAttributeAbstract, self).__init__()
        self.virtual = False
        self.data_type = None
        self.enumerable_value = False
        self.value_attr = None
        self.value_handler = None
        self.attributes = None
        self._default = kwargs.pop('default', None)
        self.journaling = kwargs.pop('journaling', True)
        self.required = bool(kwargs.pop('required', False))
        self.nullable = bool(kwargs.pop('nullable', not self.required))
        self.l10n = kwargs.pop('l10n', None)
        self.override_null = None
        self.on_new = kwargs.pop('on_new', None)
        self.on_change = kwargs.pop('on_change', None)
        self.on_text_repr = kwargs.get('on_text_repr', None)
        self.on_log_repr = kwargs.get('on_log_repr', None)
        self.setter = kwargs.pop('setter', None)
        self.getter = kwargs.pop('getter', None)
        self.in_composite_results = True
        self._caption = kwargs.pop('caption', None)
        self._abbreviation = kwargs.pop('abbreviation', None)
        self._options = kwargs.pop('options', None)
        if self.on_new is not None and not callable(self.on_new):
            raise OrmParameterError("Attributes's `on_new` must be a callable function!")
        if self.on_change is not None and not callable(self.on_change):
            raise OrmParameterError("Attributes's `on_change` must be a callable function!")

    def on_before_write(self, instance):
        """ Calls for every Model's data attribute right before starting a write procedure
        of an instance. """
        pass

    def on_after_write(self, instance):
        """ Calls for every Model's data attribute after object instance been written to
        the database, as last action. """
        pass

    def on_before_delete(self, instance, hard=None):
        """ Calls for every Model's data attribute right before starting a deletion
        procedure of an instance. """
        pass

    def on_after_delete(self, instance, hard=None):
        """ Calls for every Model's data attribute after object instance deletion occures. """
        pass

    def _l10n_text(self, s):
        """ Tries to localize given text. """
        if isinstance(self.l10n, bool):
            return s if not self.l10n else gettext(s)
        return self.l10n(s) if callable(self.l10n) else s

    def initialize(self, instance, key):
        """ Initially sets the value of this attribute. By default - calls model's
        __setattrvalue__ method to store the value directly. Datatype, based on this
        abstract class, may override this method to make some actions to store
        value correctly depending on the its logic. """
        instance.__setattrvalue__(key, self.default)

    def get_default_value(self):
        """ Returns the default value for this attribute. While default value may be
        set_value using not only static value, but also a callable function - this method
        returns a result of that callable function if it is set_value. """
        if callable(self._default):
            return self._default()
        else:
            return self._default

    def get_default_definition(self):
        """ Returns the definition of default value. Difference between this method and
        'default' property that last one will be resolved to the end value if is a
        dynamic one (is a callable function). """
        return self._default

    @property
    def default(self):
        """ Returns resolved default value for this attribute. """
        return self.get_default_value()

    @default.setter
    def default(self, value):
        """ Sets the default value definition for this attribute. """
        self._default = value

    @property
    def caption(self):
        """ The textual full-sized caption of the attribute. Not used at DBMS side. """
        return self._get_f_value('_caption', None) or self._get_f_value('_abbreviation', None) or self.model_k

    @caption.setter
    def caption(self, value):
        """ Sets the caption of this attribute. """
        self._caption = value

    @property
    def abbreviation(self):
        """ The abbreviation of the attribute. Not used at DBMS side. """
        return self._get_f_value('_abbreviation', None) or self._get_f_value('_caption', None) or self.model_k

    @abbreviation.setter
    def abbreviation(self, value):
        """ Sets the abbreviation of the attribute. """
        self._abbreviation = value

    @property
    def options(self):
        """ Set of options for the attribute. """
        from ..request import OrmRequest, REQUEST_SELECT
        from ..models import OrmModel

        value = self._get_f_value('_options', None)
        if isinstance(value, dict) or value is None:
            return value
        if isinstance(value, OrmRequest):
            if value.request_type != REQUEST_SELECT:
                raise OrmParameterError(
                    "Cannot use given request for `options` because request must be a type of OrmSelectRequest -"
                    " it must return data from the database."
                )
            rows = value.go()
            value = dict()
            for row in rows:
                k_, v_ = row.__dictpair__
                value[k_] = v_
        elif isinstance(value, str) or isinstance(value, OrmModel):
            model = mapper.get_model_by_name(value) if isinstance(value, str) else value
            if model is None:
                raise OrmInvalidKey(
                    "There is no model with name `%s` used when declaring `options`!"
                    % value
                )
            value = model.directory()
        return value

    @options.setter
    def options(self, value):
        """ Sets the defition of the options of this attribute. """
        self._options = value

    def text_repr(self, value, instance=None):
        """ Used to return human readable textual representation of the raw data of this attribute. """
        # The textual representation can be set_value to the static value, without correlation
        # to the database loaded value.
        if isinstance(self.on_text_repr, str):
            return self._l10n_text(self.on_text_repr)

        # If there is a method defined to represent the value - use it at first point.
        if callable(self.on_text_repr):
            return self._l10n_text(self.on_text_repr(value))

        # If the options list is defined - using it to try to represent the value.
        if self._options is not None:
            options = self.options
            if not options or not isinstance(options, dict):
                return self._l10n_text(value)
            if value not in options:
                return self._l10n_text(value)
            return self._l10n_text(options[value])

        # At last - return value itself.
        return "" if value is None else self._l10n_text(value)

    def log_repr(self, src, dst, instance=None):
        """ Used to return human readable textual representation of the raw value of this
        column to store to the log (history) when writting log.
        @src:               An original value which was before change;
        @dst:               A target value which been set_value;
        @return:            (tuple|list) of two values: textual representation of `value_f`
                            and textual representation of `value_t`.
        """
        # The textual representation can be set_value to the static value, without correlation
        # to the database loaded value.
        if isinstance(self.on_log_repr, str):
            return self._l10n_text(self.on_log_repr), None

        # If there is a method defined to represent the value - use it at first point.
        if callable(self.on_log_repr):
            r = self.on_log_repr(src, dst)
            if not isinstance(r, (tuple, list)) or len(r) != 2:
                raise TypeError(
                    "Custom, assigned to the column definition `log_repr` function"
                    " must return a tuple or list of two values: a textual representation"
                    " of source(from) value and destination(to) one!"
                )
            return self._l10n_text(r[0]), self._l10n_text(r[1])

        # Otherwise - return text_repr as default
        return self.text_repr(src, instance), self.text_repr(dst, instance)

    def verify(self, value):
        """ Verifies the value which about to be set to this instance's attribute. This
        method can raise 'OrmValueVerificationError' with explataion text if the value
        cannot be set, and can transform or modify value to be set, returning the
        resulting value.
        This method not sets value, but only verifies it and returns what about to be
        actually set. """
        if isinstance(value, AttributeValueNull):
            value = None
        if not value and str(value) != '0' and str(value) != '0.0' and self.required:
            raise OrmValueVerificationError(gettext('Is required'))
        if value is None and not self.nullable:
            if self.override_null is not None:
                return self.override_null
            raise OrmValueVerificationError(gettext("Must be set"))
        return value


class ColumnAttributeAbstract(OrmComparatorMixin, DataAttributeAbstract):
    """ Abstract class for DBMS driven column types """

    def __init__(self, **kwargs):
        from .columns import ColumnIntegerAbstract
        super(ColumnAttributeAbstract, self).__init__(**kwargs)
        self.is_softdelete_key = kwargs.pop('is_softdelete_key', False)
        self.is_default_order = bool(kwargs.pop('is_default_order', False))
        self.is_version_key = bool(kwargs.pop('is_version_key', False))
        self.is_caption_key = bool(kwargs.pop('is_caption_key', False))
        self.is_value_key = bool(kwargs.pop('is_value_key', False))
        self.extender_key = bool(kwargs.pop('extender_key', False))
        self.primary_key = bool(kwargs.pop('primary_key', False))
        self.auto_increment = bool(kwargs.pop('auto_increment', False))
        self.unique = kwargs.pop('unique', None)
        self.key = kwargs.pop('key', None)
        self.comment = kwargs.pop('comment', None)
        self.findable = bool(kwargs.pop('findable', False))
        self.strict_find = bool(kwargs.pop('strict_find', False))
        self.manual = bool(kwargs.pop('manual', False))
        self.references = kwargs.pop('references', None)  # reference using auto-FK on column of another OrmModel
        self.protected = bool(kwargs.pop('protected', False))
        if self.auto_increment and not isinstance(self, ColumnIntegerAbstract):
            raise OrmAttributeTypeMistake("AUTO_INCREMENT column must be the integer type!")
        if self.auto_increment:
            self.primary_key = True
            self.nullable = False
            self._default = None
        self._on_get = kwargs.pop('on_get', None)
        self._on_set = kwargs.pop('on_set', None)
        self._cast_write = kwargs.pop('cast_write', None)
        self._cast_read = kwargs.pop('cast_read', None)
        self._cast_order_by = kwargs.pop('cast_order_by', self._cast_read)
        self._cast_group_by = kwargs.pop('cast_group_by', self._cast_read)
        self._cast_filter = kwargs.pop('cast_filter', self._cast_read)
        for n in kwargs:
            if hasattr(self, n):
                continue
            v = kwargs.get(n)
            setattr(self, n, v)

    def __hash__(self):
        return super(OrmComparatorMixin, self).__hash__()

    def as_(self, name):
        """ Returns this attribute formatted to be named column as `name`. """
        return AttributeAliased(self, name)

    @staticmethod
    def _cmp_c_definition(val1, val2):
        if val1 is None and val2 is not None:
            return False
        if val1 is not None and val2 is None:
            return False
        return val1 == val2

    def alter_sql(self, session):
        pass

    def declaration_sql(self, session):
        pass

    def is_eq_with_tbl_schema(self, struct, session):
        pass

    def represent_for_write(self, value, session):
        return value

    def make_write(self, context):
        pn = context.get_valueparam_by_column(self)
        if not pn:
            return None
        if self._cast_write is not None:
            return self._cast_write(context, pn)
        if self.auto_increment and not context.params[pn]:
            return None
        return "%(" + pn + ")s"

    def make_read(self, context):
        if not self._cast_read:
            return self
        return self._cast_read(context)

    def make_filter(self, context):
        if not self._cast_filter:
            return self
        return self._cast_filter(context)

    def make_order_by(self, context):
        if not self._cast_order_by:
            return self.resolve_opts_to_case()
        return self._cast_order_by(context)

    def make_group_by(self, context):
        if not self._cast_group_by:
            return self
        return self._cast_group_by(context)

    def resolve_opts_to_case(self):
        from ..funcs import case_else_
        options = self.options
        if not options:
            return self
        fargs = list()
        for k in options:
            v = options[k]
            fargs.append((k, v))
        return case_else_(self, "", *fargs)

    @staticmethod
    def _find_prepare(value):
        return value

    def find_prepare(self, value):
        if isinstance(value, (list, tuple)):
            r = list()
            for val in value:
                v = self._find_prepare(val)
                if not v:
                    continue
                r.append(str(v))
            return r
        else:
            return self._find_prepare(value)


class VirtualAttributeAbstract(DataAttributeAbstract):
    """ Abstract class for virtual attributes, not directly reflected at DBMS """
    def write(self, instance, key):
        pass


class KeyAttributeAbstract(AttributeAbstract):
    def __init__(self, *args):
        if not args:
            raise OrmParameterError("No _attrs are specified when declaring KEY `%s`!" % self.model_k)
        super(KeyAttributeAbstract, self).__init__()
        self._validated = False
        self._args = args
        self.columns = list()

    def validate(self):
        if self._validated:
            return
        for arg in self._args:
            if not isinstance(arg, (str, ColumnAttributeAbstract)):
                raise OrmParameterError(
                    "When declaring KEYs: _attrs must be set using textual names (str) or attributes themselfs."
                )
            if isinstance(arg, str):
                if not hasattr(self.model, arg):
                    raise OrmInvalidKey(
                        "OrmModel `%s` has no attribute `%s` set for the key `%s`!" %
                        (self.model.__name__, arg, self.model_k)
                    )
                c = getattr(self.model, arg)
                if not isinstance(c, ColumnAttributeAbstract):
                    raise OrmAttributeTypeMistake(
                        "Attribute `%s` in the OrmModel `%s`, declaring in the key `%s`, is not a type of"
                        " Column! Only database table refrected attributes may be setattr for keys!" %
                        (arg, self.model.__name__, self.model_k)
                    )
                self.columns.append(arg)
            else:
                if arg.model != self.model:
                    raise OrmAttributeTypeMistake(
                        "Attribute `%s` is not belongs to the OrmModel `%s`, declaring in the key `%s`!"
                        " Only local OrmModel's attributes may be set for OrmModel's keys!" %
                        (arg, self.model.__name__, self.model_k)
                    )
                self.columns.append(arg.model_k)
        self._validated = True

    def get_column_names(self, quoted=False, session=None):
        """ Returns the list() of names of all keys of this unique keys """
        names = []
        for k in self.columns:
            c = getattr(self.model, k)
            n = c.tbl_k
            if quoted:
                n = session.quote_name(n)
            names.append(n)
        return names


class AttributeAliased(object):
    """ Aliases the attribute with another name. Useful with <>.as_() method, for example """
    def __init__(self, c, alias):
        self.c = c
        self.alias = alias

    def __repr__(self):
        return "AlisedAttr(%r AS '%s')" % (self.c, self.alias)


def _attribute(c, **kwargs):
    """ A virtual attribute declaration which receives an existing actual attribute
    definition as argument and modifiers as named arguments. Used to set_value up
    an existing attribute somewhere else, with posibility to redefine some
    attribute parameters.
    @c:             An existing attribute, already been declared before;
    @kwargs:        Optional modifiers which may change some parameters of the
                    newly declared attribute, which differs from the original one.
    """
    mc = copy.copy(c)
    for k in kwargs:
        setattr(mc, k, kwargs[k])
    return mc


Attribute = _attribute


def _caption(*args, **kwargs):
    from .derived import CaptionString
    if args and isinstance(args[0], AttributeAbstract):
        return Attribute(args[0], is_caption_key=True, **kwargs)
    return CaptionString(*args, **kwargs)


Caption = _caption

