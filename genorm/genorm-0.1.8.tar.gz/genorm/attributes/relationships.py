import copy
from pc23 import xrange
from ..exceptions import OrmParameterError, OrmAttributeTypeMistake, OrmInvalidKey, OrmDefinitionError, \
    OrmModelDeclarationError
from ..mapper import mapper
from ..manage import manager
from ..values.relationships import ValueRelatedToOne, ValueRelatedToMany, ValueManyToMany
from .base import OrmComparatorMixin, AttributeAliased, AttributeAbstract, KeyAttributeAbstract, \
    ColumnAttributeAbstract, DataAttributeAbstract, FK_ONDELETE_CASCADE, FK_ONDELETE_SET_NULL


class ForeignKeyConstraintAbstract(KeyAttributeAbstract):
    def __init__(self, *args, **kwargs):
        if len(args) != 2:
            raise OrmParameterError(
                "Relationships requires pairs of _attrs to be specified! For complex relationships, when"
                " more than one column from each of OrmModel participates, they must be grouped using (list)"
                " or (tuple)."
            )
        if (isinstance(args[0], (list, tuple)) and not isinstance(args[1], (list, tuple))) \
                or (isinstance(args[1], (list, tuple)) and not isinstance(args[0], (list, tuple))):
            raise OrmParameterError(
                "Complex relationships cannot be declared with different quantity of _attrs for"
                " one and for another Models! Local and referenced _attrs must be declared by pairs!"
            )
        if isinstance(args[0], (list, tuple)) and len(args[0]) != len(args[1]):
            raise OrmParameterError(
                "Complex relationships cannot be declared with different quantity of _attrs for"
                " one and for another Models! Local and referenced _attrs must be declared by pairs!"
            )
        super(ForeignKeyConstraintAbstract, self).__init__(*args)
        self.on_delete = kwargs.pop('on_delete', None)
        self.on_update = kwargs.pop('on_update', None)
        self.ref_model = None
        self.ref_columns = list()

    def validate(self):
        if self._validated:
            return
        local_args = self._args[0] if isinstance(self._args[0], (list, tuple)) else (self._args[0], )
        ref_args = self._args[1] if isinstance(self._args[1], (list, tuple)) else (self._args[1],)
        ref_model_name = None
        for arg in local_args:
            if not isinstance(arg, (str, ColumnAttributeAbstract)):
                raise OrmParameterError(
                    "Columns in relationship declarations must be set using textual names (str) or attributes"
                    " themselfs."
                )
            if isinstance(arg, str) and '.' in arg:
                raise OrmAttributeTypeMistake(
                    "Local (for OrmModel) _attrs, defined for relationships, cannot be specified with"
                    " OrmModel name part ('OrmModel.attribute_name'), but must be specified using only attribute"
                    " name ('attribute_name')!"
                )
            k = arg if isinstance(arg, str) else arg.model_k
            if not hasattr(self.model, k):
                raise OrmInvalidKey(
                    "OrmModel '%s' has no attribute '%s' set for the relationship '%s'!" %
                    (self.model.__name__, k, self.model_k)
                )
            c = getattr(self.model, k)
            if not isinstance(c, ColumnAttributeAbstract):
                raise OrmAttributeTypeMistake(
                    "Attribute '%s' in the OrmModel '%s', declaring in the key '%s', is not a type of"
                    " Column! Only database table refrected attributes may be set for keys!" %
                    (k, self.model.__name__, self.model_k)
                )
            self.columns.append(k)
        for arg in ref_args:
            if not isinstance(arg, (str, ColumnAttributeAbstract)):
                raise OrmParameterError(
                    "Columns in relationship declarations must be set using textual names (str) or attributes"
                    " themselfs."
                )
            if isinstance(arg, str) and '.' not in arg:
                raise OrmAttributeTypeMistake(
                    "Referencing _attrs, defined for relationships, must be specified with"
                    " OrmModel name part ('OrmModel.attribute_name')!"
                )
            if isinstance(arg, str):
                p = arg.split('.')
                if len(p) != 2:
                    raise OrmAttributeTypeMistake(
                        "Referencing _attrs, defined for relationships, must be specified with"
                        " OrmModel name part ('OrmModel.attribute_name')!"
                    )
                attr_ref_model = p[0]
                if ref_model_name and ref_model_name != attr_ref_model:
                    raise OrmParameterError("There can be only one referencing OrmModel for relationship!")
                elif not ref_model_name:
                    ref_model_name = attr_ref_model
                    self.ref_model = mapper.get_model_by_name(ref_model_name)
                k = p[1]
                if not hasattr(self.ref_model, k):
                    raise OrmInvalidKey(
                        "OrmModel `%s` has no attribute `%s` set for the relationship `%s`!" %
                        (self.ref_model.__name__, k, self.model_k)
                    )
                c = getattr(self.ref_model, k)
                if not isinstance(c, ColumnAttributeAbstract):
                    raise OrmAttributeTypeMistake(
                        "Attribute `%s` in the OrmModel `%s`, declaring in the key `%s`, is not a type of"
                        " Column! Only database table refrected attributes may be set for keys!" %
                        (k, self.model.__name__, self.model_k)
                    )
            else:
                attr_ref_model = arg.model.__name__
                if ref_model_name and ref_model_name != attr_ref_model:
                    raise OrmParameterError("There can be only one referencing OrmModel for relationship!")
                elif not ref_model_name:
                    ref_model_name = attr_ref_model
                    self.ref_model = mapper.get_model_by_name(ref_model_name)
                k = arg.model_k
                if not isinstance(arg, ColumnAttributeAbstract):
                    raise OrmAttributeTypeMistake(
                        "Attribute `%s` in the OrmModel `%s`, declaring in the key `%s`, is not a type of"
                        " Column! Only database table refrected attributes may be set for keys!" %
                        (k, self.model.__name__, self.model_k)
                    )
            self.ref_columns.append(k)
        self._validated = True

    @property
    def key_name(self):
        return "%s_ibfk_%s" % (self.model.table, self.tbl_k)


class ForeignKey(ForeignKeyConstraintAbstract):
    """ Foreign key constraint which refrecting at the database table. """
    def declaration_sql(self, session):
        self.validate()
        fk_name = self.tbl_k
        fk_l = []
        fk_r = []
        fk_sz = len(self.columns)
        for i in xrange(fk_sz):
            fk_l_ = self.columns[i]
            fk_r_ = self.ref_columns[i]
            fk_cl_ = getattr(self.model, fk_l_)
            fk_cr_ = getattr(self.ref_model, fk_r_)
            fk_l.append(session.quote_name(fk_cl_.tbl_k))
            fk_r.append(session.quote_name(fk_cr_.tbl_k))
        fk_table = self.ref_model.table
        fk_left = ",".join(fk_l)
        fk_right = ",".join(fk_r)
        fkq = "CONSTRAINT %s FOREIGN KEY (%s) REFERENCES %s(%s)" % \
              (session.quote_name(fk_name), fk_left, session.quote_name(fk_table), fk_right)
        if self.on_delete:
            fkq += " ON DELETE " + str(self.on_delete).upper()
        if self.on_update:
            fkq += " ON UPDATE " + str(self.on_update).upper()
        return fkq

    def declaration_key_sql(self, session):
        self.validate()
        fk_name = self.tbl_k
        fk_l = []
        fk_sz = len(self.columns)
        for i in xrange(fk_sz):
            fk_l_ = self.columns[i]
            fk_cl_ = getattr(self.model, fk_l_)
            fk_l.append(session.quote_name(fk_cl_.tbl_k))
        fk_left = ",".join(fk_l)
        return "KEY %s (%s)" % (session.quote_name(fk_name), fk_left)


class VirtualForeignKey(ForeignKeyConstraintAbstract):
    """ Virtual relationship which is actual for ORM mechanics same as foreign keys, but
    not reflecting at the database table. """
    pass


class Relationship(AttributeAbstract):
    """ A special kind of attribute which make a relationship between two Models - the one
    where it is declared at, and the second which is specified as a first parameter. This
    attribute analyses the destination OrmModel and creates local attribute with the same
    type and secondary parameters as at destination OrmModel, so the programmer have not to
    care about correct type of local attribute (which must be compatible with foreign
    attribute at foreign OrmModel otherwise). Besides, this attribute automatically declare
    a foreign key in the local OrmModel, connecting it with foreign OrmModel using local
    attribute.
    A destination (foreign side) can be set using:
    a) a textual name of the attribute in the format 'foreign_Model_name.attribute_name';
    b) a testual name of the foreign OrmModel 'foreign_Model_name';
    c) an attribute itself: `ForeignModel.attribute_name`;
    d) a foreign OrmModel itself: `ForeignModel`;
    When no foreign attribute is set - ORM will take a primary key of the foreign
    OrmModel and use it as foreign attribute.
    """
    def __init__(self, foreign_attribute, on_delete=None, on_update=None, **kwargs):
        super(Relationship, self).__init__()
        self.on_delete = on_delete
        self.on_update = on_update
        self.foreign_attribute = foreign_attribute
        self.kw = kwargs

    @staticmethod
    def _deferred_make(local_model, local_k, foreign_model, foreign_k, **kwargs):
        local_model = mapper.get_model_by_name(local_model)
        foreign_model = mapper.get_model_by_name(foreign_model)
        if foreign_k is None:
            foreign_pks = foreign_model.__meta__.primary_key
            if len(foreign_pks) != 1:
                raise OrmParameterError(
                    "(Relationship) can make relationship using only simple pair of local and"
                    " foreign attributes, but given foreign OrmModel has complex primary key defined!"
                )
            foreign_k = foreign_pks[0]
        local_c = getattr(local_model, local_k)
        foreign_c = getattr(foreign_model, foreign_k)
        if not isinstance(foreign_c, ColumnAttributeAbstract):
            raise OrmParameterError(
                "(Relationship) type attribute requries that foreign attribute which this pointer is"
                " pointing at to be a type of: a) (str) in format 'Model_name.attribute_name';"
                " b) (str) in format 'Model_name' - then OrmModel's primary key will be taken as"
                " a destination attribute; c) an attribute itself or d) a OrmModel - then OrmModel's"
                " primary key will be taken as a destination attribute!"
            )
        fk_type = VirtualForeignKey if isinstance(local_c, VirtualRelationship) else ForeignKey
        on_delete = local_c.on_delete
        on_update = local_c.on_update
        foreign_c_type = foreign_c.base_type or foreign_c.__class__
        override_c = foreign_c_type()
        override_c.__dict__ = copy.deepcopy(foreign_c.__dict__)
        override_c.primary_key = False
        override_c.auto_increment = False
        override_c.tbl_k = local_c.tbl_k
        override_c.declaration_order = local_c.declaration_order
        override_c.nullable = kwargs.pop('nullable', True)
        if foreign_c.primary_key:
            override_c.default = None
        kwargs.pop('auto_increment', None)
        kwargs.pop('primary_key', None)
        kwargs.pop('tbl_k', None)
        for k in kwargs:
            setattr(override_c, k, kwargs[k])
        setattr(local_model, local_k, override_c)
        fk_c = fk_type(override_c, foreign_c, on_delete=on_delete, on_update=on_update)
        fk_k = "fk_%s_" % local_k
        setattr(local_model, fk_k, fk_c)
        override_c.foreign_key = fk_c

    def on_declare(self):
        from ..models.meta import OrmModelMeta
        from ..models.base import OrmModelAbstract
        if isinstance(self.foreign_attribute, str):
            p = self.foreign_attribute.split('.')
            if len(p) > 2:
                raise OrmParameterError(
                    "(Relationship) type attribute requries that foreign attribute which this pointer is"
                    " pointing at to be a type of: a) (str) in format 'Model_name.attribute_name';"
                    " b) (str) in format 'Model_name' - then OrmModel's primary key will be taken as"
                    " a destination attribute; c) an attribute itself or d) a OrmModel - then OrmModel's"
                    " primary key will be taken as a destination attribute!"
                )
            foreign_model_name = p[0]
            foreign_k = p[1] if len(p) == 2 else None
        elif isinstance(self.foreign_attribute, ColumnAttributeAbstract):
            foreign_model_name = self.foreign_attribute.model.__name__
            foreign_k = self.foreign_attribute.model_k
        elif isinstance(self.foreign_attribute, (OrmModelMeta, OrmModelAbstract)):
            foreign_model_name = self.foreign_attribute.__name__
            foreign_k = None
        else:
            raise OrmParameterError(
                "(Relationship) type attribute required that first argument to be a name of foreign"
                " attribute in format 'OrmModel.attribute_name' or a foreign attribute itself!"
            )
        args = (self.model.__name__, self.model_k, foreign_model_name, foreign_k)
        kwargs = self.kw
        mapper.register_on_model_declare(foreign_model_name, self._deferred_make, *args, **kwargs)


class VirtualRelationship(Relationship):
    pass


class RelatedAbstract(AttributeAbstract):
    def __init__(self, foreign, on_delete=None, **kwargs):
        super(RelatedAbstract, self).__init__()
        self._validated = False
        self.foreign = foreign
        self.foreign_model = None
        self.foreign_k = None
        self.foreign_c = None
        self.on_delete = on_delete
        self._caption = kwargs.pop('caption', None)
        self._abbreviation = kwargs.pop('abbreviation', None)

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

    def on_model_declared(self):
        if isinstance(self.foreign, AttributeAbstract):
            self.foreign = "%s.%s" % (self.foreign.model.__name__, self.foreign.model_k)

    def validate(self):
        from ..models.meta import OrmModelMeta
        from ..models.base import OrmModelAbstract
        if self._validated:
            return
        if isinstance(self.foreign, str):
            if '.' in self.foreign:
                p = self.foreign.split('.')
                if len(p) != 2:
                    raise OrmParameterError(
                        "Related pointers must be set using OrmModel wich has corresponding relationship with"
                        " this model declared, or using format `OrmModel.key` where `key` can be a relationship or"
                        " foreign key describing the relationship between foreign model and this one!"
                    )
                ref_model_name_ = p[0]
                ref_k_ = p[1]
                if not ref_model_name_ or not ref_k_:
                    raise OrmParameterError(
                        "Related pointers must be set using OrmModel wich has corresponding relationship with"
                        " this model declared, or using format `OrmModel.key` where `key` can be a relationship or"
                        " foreign key describing the relationship between foreign model and this one!"
                    )
                ref_model_ = mapper.get_model_by_name(ref_model_name_)
                if not ref_model_:
                    raise OrmParameterError(
                        "Related pointer referencing unknown OrmModel name: `%s`!" % ref_model_name_
                    )
                if not hasattr(ref_model_, ref_k_):
                    raise OrmParameterError(
                        "Related pointer referencing unknown OrmModel's attribute: `%s`.`%s`!" %
                        (ref_model_name_, ref_k_)
                    )
                foreign_c_ = getattr(ref_model_, ref_k_)
                if getattr(foreign_c_, 'foreign_key', None):
                    foreign_c_ = foreign_c_.foreign_key
                foreign_c_.validate()
                foreign_model_ = foreign_c_.ref_model if foreign_c_.ref_model != self.model else foreign_c_.model
            elif mapper.has_model(self.foreign):
                foreign_model_name_ = self.foreign
                foreign_model_ = mapper.get_model_by_name(foreign_model_name_)
                if not foreign_model_:
                    raise OrmParameterError(
                        "Related pointer referencing unknown OrmModel name: `%s`!" % foreign_model_name_
                    )
                foreign_c_ = foreign_model_.__meta__.get_relationship_with_model(self.model)
                if foreign_c_ is None and not foreign_model_.__meta__.foreign:
                    foreign_c_ = foreign_model_.__meta__.make_relationship_with_model(
                        self.model, on_delete=self.on_delete)
                if foreign_c_ is None:
                    raise OrmParameterError(
                        "Related pointer referencing OrmModel `%s` which has no declared relationship key with"
                        " this OrmModel!" % foreign_model_name_
                    )
                elif foreign_c_ is True:
                    raise OrmParameterError(
                        "Related pointer referencing OrmModel `%s` which has more than one unique relationship"
                        " with this OrmModel! Is this case there must be a referencing attribute to be specified"
                        " using format `OrmModel.attribute`!"
                    )
                foreign_c_.validate()
            else:
                ref_k_ = self.foreign
                if not hasattr(self.model, ref_k_):
                    raise OrmParameterError(
                        "Related pointer referencing OrmModel `%s` which has more than one unique relationship"
                        " with this OrmModel! Is this case there must be a referencing attribute to be specified"
                        " using format `OrmModel.attribute`!"
                    )
                foreign_c_ = getattr(self.model, ref_k_)
                if getattr(foreign_c_, 'foreign_key', None):
                    foreign_c_ = foreign_c_.foreign_key
                foreign_c_.validate()
                foreign_model_ = foreign_c_.ref_model
        elif isinstance(self.foreign, (OrmModelMeta, OrmModelAbstract)):
            foreign_model_name_ = self.foreign.__class__.__name__
            foreign_model_ = self.foreign
            foreign_c_ = foreign_model_.__meta__.get_relationship_with_model(self.model)
            if foreign_c_ is None:
                raise OrmParameterError(
                    "Related pointer referencing OrmModel `%s` which has no declared relationship key with"
                    " this OrmModel!" % foreign_model_name_
                )
            elif foreign_c_ is True:
                raise OrmParameterError(
                    "Related pointer referencing OrmModel `%s` which has more than one unique relationship"
                    " with this OrmModel! Is this case there must be a referencing attribute to be specified"
                    " using format `OrmModel.attribute`!"
                )
            foreign_c_.validate()
        elif isinstance(self.foreign, ForeignKeyConstraintAbstract):
            foreign_model_ = self.foreign.model
            foreign_c_ = self.foreign
            foreign_c_.validate()
        else:
            raise OrmParameterError(
                "Related pointers must be set using OrmModel wich has corresponding relationship with this"
                " model declared, or using format `OrmModel.key` where `key` can be a relationship or"
                " foreign key describing the relationship between foreign model and this one!"
            )
        if getattr(foreign_c_, 'foreign_key', None):
            foreign_c_ = foreign_c_.foreign_key
        self.foreign_model = foreign_model_
        self.foreign_c = foreign_c_
        self.foreign_c.validate()
        self._validated = True


class RelatedToOneAbstract(RelatedAbstract):
    def __init__(self, foreign, on_delete=None, always_deferred=False, **kwargs):
        super(RelatedToOneAbstract, self).__init__(foreign, on_delete=on_delete, **kwargs)
        self.always_deferred = bool(always_deferred)

    def initialize(self, instance, k):
        virtual_value = ValueRelatedToOne()
        virtual_value.model_k = k
        virtual_value.instance = instance
        virtual_value.c = self
        instance.__setattrabs__(k, virtual_value)


class RelatedToManyAbstract(RelatedAbstract):
    def initialize(self, instance, k):
        virtual_value = ValueRelatedToMany()
        virtual_value.model_k = k
        virtual_value.instance = instance
        virtual_value.c = self
        instance.__setattrabs__(k, virtual_value)


class OneToOne(RelatedToOneAbstract):
    pass


class ManyToOne(RelatedToOneAbstract):
    pass


class OneToMany(RelatedToManyAbstract):
    pass


class UserIdentAbstract(ManyToOne):
    def __init__(self, **kwargs):
        self.ident_k = None
        super(UserIdentAbstract, self).__init__(None, on_delete=FK_ONDELETE_SET_NULL, **kwargs)

    def on_model_declared(self):
        foreign = manager.get_user_ident()
        fmodel = mapper.get_model_by_name(foreign) if isinstance(foreign, str) else foreign
        fpk = fmodel.__meta__.get_primary_key()
        if len(fpk) > 1:
            raise OrmModelDeclarationError("user ident's Model must not have complex primary key!")
        fpk = fpk[0]
        foreign = "%s.%s" % (fmodel.__name__, fpk.model_k)
        c = Relationship(foreign, on_delete=FK_ONDELETE_SET_NULL)
        c.declaration_order = 15
        k = "%s_id" % self.model_k
        setattr(self.model, k, c)
        self.foreign = k
        self.ident_k = k
        super(UserIdentAbstract, self).on_model_declared()

    def validate(self):
        super(UserIdentAbstract, self).validate()


class AuthorIdent(UserIdentAbstract):
    """ This attribute will be set to the current session user ID/UUID when the object is a new one
    and only inserting to the database - the initial author of the object. """
    def on_model_declared(self):
        super(AuthorIdent, self).on_model_declared()
        self.model.__meta__.author_ident.append(self)


class PerformerIdent(UserIdentAbstract):
    """ This attribute will be set to the current session user ID/UUID always when object writes,
    not matter - is the object new or not. """
    def on_model_declared(self):
        super(PerformerIdent, self).on_model_declared()
        self.model.__meta__.performer_ident.append(self)


class UserIdent(UserIdentAbstract):
    """ The custom user ident attribute - it will not automatically be set to anything. """
    pass


class ManyToMany(AttributeAbstract):
    def __init__(self, model_a, model_b, on_delete=FK_ONDELETE_CASCADE):
        from ..models.meta import OrmModelMeta
        from ..models.base import OrmModel
        if not isinstance(model_a, (OrmModelMeta, OrmModel, str)) \
                or not isinstance(model_b, (OrmModelMeta, OrmModel, str)):
            raise OrmParameterError(
                "`ManyToMany` requires that the first and second arguments be of type (OrmModel|str)!"
            )
        if on_delete == FK_ONDELETE_SET_NULL:
            raise OrmParameterError("`ManyToMany`.`on_delete` cannot be `SET NULL`!")
        super(ManyToMany, self).__init__()
        self.model_a = model_a.__name__ if isinstance(model_a, (OrmModelMeta, OrmModel)) else model_a
        self.model_b = model_b.__name__ if isinstance(model_b, (OrmModelMeta, OrmModel)) else model_b
        self.on_delete = on_delete
        self.junction_model = None
        self.key = mapper.register_many2many(self, model_a, model_b)
        self._validated = False

    def validate(self, jmodel=None):
        if self._validated:
            return
        if self.key is None:
            return
        model = jmodel if jmodel is not None else mapper.get_many2many_junction_model(self.key)
        if not model:
            raise OrmDefinitionError(
                "`ManyToMany`.`validate` been called before Many-To-Many relationship initialized!"
            )
        attrs = dir(model)
        for k in attrs:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = getattr(model, k)
            if not isinstance(c, ForeignKeyConstraintAbstract):
                continue
            c.validate()
        self.junction_model = model
        self._validated = True

    def initialize(self, instance, k):
        virtual_value = ValueManyToMany()
        virtual_value.model_k = k
        virtual_value.instance = instance
        virtual_value.c = self
        instance.__setattrabs__(k, virtual_value)

    def is_assigned(self, f_instance):  # Abstract
        pass

    def find(self, *args, **kwargs):  # Abstract
        pass

    def add(self, *args, **kwargs):  # Abstract
        pass

    def delete(self, *args, **kwargs):  # Abstract
        pass

    def write(self, session=None, force=False):  # Abstract
        pass



class ForeignAttr(OrmComparatorMixin, DataAttributeAbstract):
    def __init__(self, related_attr, referenced_k=None, **kwargs):
        if not isinstance(related_attr, (str, RelatedToOneAbstract)):
            raise OrmParameterError(
                "ForeignColumn 'related_attr' parameter must be a type of (str) or ...ToOne relationship!"
            )
        self._related_attr = related_attr
        self._related_k = None
        self._ref_k = referenced_k
        super(ForeignAttr, self).__init__(**kwargs)
        self._custom_getter = self.getter
        self._custom_setter = self.setter
        self.getter = self._getter
        self.setter = self._setter

    def __hash__(self):
        return super(OrmComparatorMixin, self).__hash__()

    def as_(self, name):
        """ Returns this attribute formatted to be named column as `name`. """
        return AttributeAliased(self, name)

    @property
    def related_k(self):
        if self._related_k:
            return self._related_k
        if not isinstance(self._related_attr, (str, RelatedToOneAbstract)):
            raise OrmParameterError(
                "ForeignColumn 'related_attr' parameter must be a type of (str) or ...ToOne relationship!"
            )
        self._related_k = self._related_attr if isinstance(self._related_attr, str) else self._related_attr.model_k
        return self._related_k

    @property
    def referenced_k(self):
        return self._ref_k if self._ref_k else self.model_k

    def _getter(self, instance, k):
        if not hasattr(instance, self.related_k):
            raise OrmDefinitionError(
                "model '%s' has no relationship with name '%s' for foreign attribute '%s'" %
                (self.model.__name__, self._related_k, self.model_k)
            )
        ref_instance = getattr(instance, self.related_k)
        return getattr(ref_instance, self.referenced_k)

    def _setter(self, instance, k, value, on_instance_loaded=False):
        if not hasattr(instance, self.related_k):
            raise OrmDefinitionError(
                "model '%s' has no relationship with name '%s' for foreign attribute '%s'" %
                (self.model.__name__, self._related_k, self.model_k)
            )
        ref_instance = getattr(instance, self.related_k)
        return ref_instance.__setattr__(self.referenced_k, value)


