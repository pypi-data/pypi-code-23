from collections import OrderedDict
from ..attributes.base import AttributeAbstract, ColumnAttributeAbstract, KeyAttributeAbstract,\
    VirtualAttributeAbstract, DataAttributeAbstract
from ..values import AttributeValueVirtual
from ..attributes.relationships import RelatedAbstract, ManyToMany, Relationship, VirtualRelationship, ForeignAttr, \
    RelatedToOneAbstract, ForeignKeyConstraintAbstract, OneToMany, FK_ONDELETE_SET_NULL
from ..exceptions import OrmParameterError


class OrmModelMetaStruct(object):
    def __init__(self, cls):
        self.PROTECTED = ('cls', 'auto_increment', 'primary_key')
        self.tag = None
        self.session = None
        self.cls = cls
        self.tablename = None
        self.prefix = None
        self.primary_key = None
        self.auto_increment = None
        self.userident = False
        self.soft_delete = None
        self.default_order = None
        self.version_key = None
        self.caption_key = None
        self.value_key = None
        self.initial = None
        self.on_before_write = None
        self.on_after_write = None
        self.on_insert = None
        self.on_update = None
        self.on_change = None
        self.on_before_delete = None
        self.on_after_delete = None
        self.on_instance_create = None
        self.on_instance_loaded = None
        self.constructor = None
        self.log = None
        self.foreign = False
        self.foreign_keys = list()
        self.unique_keys = list()
        self.index_keys = list()
        self.relationships = list()
        self.author_ident = list()
        self.performer_ident = list()
        self.timestamp_creation = list()
        self.timestamp_modification = list()

    def get_model_struct(self):
        """ Returns the structure of this OrmModel, which describes defined attributes:
        attributes, keys (including foreign keys), primary key and etc. This method is using
        at a moment of database migration mechanism, for example. """
        return {
            'columns': self.get_column_attributes_dict(),
            'indexes': self.get_index_keys_dict(),
            'foreign_keys': self.get_foreign_keys_dict(),
            'unique_keys': self.get_unique_keys_dict(),
            'primary_key': self.get_primary_key()
        }

    def get_primary_key(self):
        """ Returns primary key (list of attributes) of the Model. """
        pk = []
        for k in self.primary_key:
            pk.append(getattr(self.cls, k))
        return pk

    def get_autoincrement(self):
        """ Returns auto-increment attribute if one defined, None otherwise. """
        return getattr(self.cls, self.auto_increment) if self.auto_increment else None

    def get_attributes(self):
        """ Returns a list of attributes of the Model (attributes themself, not keys). """
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, AttributeAbstract):
                continue
            attrs_.append((c.declaration_order, c))
        if not attrs_:
            return []
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_attributes_keys(self):
        """ Returns a list of attributes' names (keys) of the Model. """
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, AttributeAbstract):
                continue
            attrs_.append((c.declaration_order, k))
        if not attrs_:
            return []
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_real_attributes(self):
        """ Returns a list of attributes which has direct reflection in the database table
        (attributes themself, not keys). """
        attrs = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, (ColumnAttributeAbstract, KeyAttributeAbstract)):
                continue
            attrs.append(c)
        return attrs

    def get_data_attributes(self):
        """ Returns a list of data attributes (attributes which holding some kind of data, attributes
        themselfs, not keys). """
        attrs = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, DataAttributeAbstract):
                continue
            attrs.append(c)
        return attrs

    def get_findable_attributes(self):
        """ Returns a list of findable attributes, which has property 'findable' set to True -- only
        'real' attributes which are reflecting to the database table (attributes themself, not keys). """
        attrs = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, ColumnAttributeAbstract):
                continue
            if not c.findable:
                continue
            attrs.append(c)
        return attrs

    def get_related_attributes(self):
        """ Returns a list of relationships of any X-to-X type , attributes themself, not keys. """
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, RelatedAbstract):
                continue
            attrs_.append((c.declaration_order, c))
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_related_to_one_attributes(self):
        """ Returns a list of relationships of type ...ToOne (OneToOne and ManyToOne), attributes
        themself, not keys. """
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, RelatedToOneAbstract):
                continue
            attrs_.append((c.declaration_order, c))
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_related_using_fk(self, fk):
        """ Returns a list of relationship attributes (..ToOne) which using given ForeignKey,
        attributes themself, not keys. """
        if isinstance(fk, str):
            fkc = getattr(self.cls, fk, None)
            if fkc is None:
                raise OrmParameterError(
                    "get_related_using_fk() requires that 'fk' argument be a type of (str) -- the name of"
                    " the corresponding ForeignKey attribute, or ForeignKey attribute itself!"
                )
        elif not isinstance(fk, ForeignKeyConstraintAbstract):
            raise OrmParameterError(
                "get_related_using_fk() requires that 'fk' argument be a type of (str) -- the name of"
                " the corresponding ForeignKey attribute, or ForeignKey attribute itself!"
            )
        else:
            fkc = fk
        attrs_ = list()
        rattrs = self.get_related_attributes()
        for c in rattrs:
            c.validate()
            if c.foreign_c != fkc:
                continue
            attrs_.append((c.declaration_order, c))
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_attributes_for_select(self):
        """ Returns a list of attributes used in selecing request (returns 'real' attributes, themself,
        not keys, which are directly reflected in database table and has corresponding single columns). """
        from ..funcs import DbFunctionAbstract
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, (DataAttributeAbstract, DbFunctionAbstract)):
                continue
            if isinstance(c, ForeignAttr):
                continue
            if isinstance(c, DataAttributeAbstract) and c.virtual:
                continue
            attrs_.append((c.declaration_order, c))
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_attributes_for_write(self):
        """ Returns a list of attributes used in modify requests (UPDATE and INSERT) -- 'real'
        attributes which has direct reflection in database table (attributes themself, not keys). """
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, ColumnAttributeAbstract):
                continue
            attrs_.append((c.declaration_order, c))
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_keys_for_write(self):
        """ Returns a list of attributes' keys used in modify requests (UPDATE and INSERT) -- 'real'
        attributes which has direct reflection in database table (Keys only). """
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, ColumnAttributeAbstract):
                continue
            attrs_.append((c.declaration_order, k))
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_virtualkeys_for_write(self, instance):
        """ Returns a list of virtual attributes' keys which has routines for writting and
        been already loaded at a time of Model instance writting. """
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, VirtualAttributeAbstract):
                continue
            v = instance.__getattrabs__(k)
            is_loaded = getattr(v, '_loaded', True)
            if not is_loaded:
                continue
            attrs_.append((c.declaration_order, k))
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_related_loaded_attributes(self, instance):
        """ Returns a list of relationship attributes (X-To-X) which been loaded
        from the database (initially some attributes not loaded from database -- for
        example, ManyToMany and OneToMany, and loads only when trying to read them
        in the program code, saving some server resources). Relationships which
        not been loaded not fall into this list. """
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, (RelatedAbstract, ManyToMany)):
                continue
            v = instance.__getattrabs__(k)
            if isinstance(v, AttributeValueVirtual):
                continue
            attrs_.append((c.declaration_order, c))
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_related_loaded_keys(self, instance):
        """ Returns a list of relationship attributes' keys (X-To-X) which been loaded
        from the database (initially some attributes not loaded from database -- for
        example, ManyToMany and OneToMany, and loads only when trying to read them
        in the program code, saving some server resources). Relationships which
        not been loaded not fall into this list. """
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, (RelatedAbstract, ManyToMany)):
                continue
            v = instance.__getattrabs__(k)
            if not isinstance(v, AttributeValueVirtual):
                continue
            if not v.loaded:
                continue
            attrs_.append((c.declaration_order, k))
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_foreign_attrs(self):
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, ForeignAttr):
                continue
            attrs_.append((c.declaration_order, c))
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_foreign_attrs_keys(self):
        attrs_ = list()
        keys = dir(self.cls)
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = type.__getattribute__(self.cls, k)
            if not isinstance(c, ForeignAttr):
                continue
            attrs_.append((c.declaration_order, k))
        return [y[1] for y in sorted(attrs_, key=lambda x: x[0])]

    def get_foreign_attrs_by_relationships(self):
        foreign_attrs = self.get_foreign_attrs()
        rel_cc = dict()
        for c in foreign_attrs:
            c.validate()
            related_k = c.related_k
            rel_c = getattr(self.cls, related_k)
            rel_c.validate()
            if rel_c not in rel_cc:
                rel_cc[rel_c] = list()
            rel_cc[rel_c].append(c)
        return rel_cc

    def get_relationships(self):
        cc = list()
        for k in self.relationships:
            cc.append(getattr(self.cls, k))
        return cc

    def get_column_attributes(self):
        attrs = dir(self.cls)
        raw_c = list()
        for k in attrs:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = getattr(self.cls, k)
            if not isinstance(c, ColumnAttributeAbstract):
                continue
            raw_c.append(c)
        return sorted(raw_c, key=lambda c_: getattr(c_, 'declaration_order', 65535))

    def get_column_attributes_dict(self):
        cc = self.get_column_attributes()
        dc = OrderedDict()
        for c in cc:
            dc[c.model_k] = c
        return dc

    def get_foreign_keys(self):
        cc = list()
        for k in self.foreign_keys:
            c = getattr(self.cls, k)
            c.validate()
            cc.append(c)
        return cc

    def get_foreign_keys_dict(self):
        cc = self.get_foreign_keys()
        dc = dict()
        for c in cc:
            dc[c.model_k] = c
        return dc

    def get_unique_keys(self):
        cc = list()
        for k in self.unique_keys:
            c = getattr(self.cls, k)
            c.validate()
            cc.append(c)
        return cc

    def get_unique_keys_dict(self):
        cc = self.get_unique_keys()
        dc = dict()
        for c in cc:
            dc[c.model_k] = c
        return dc

    def get_index_keys(self):
        cc = list()
        for k in self.index_keys:
            c = getattr(self.cls, k)
            c.validate()
            cc.append(c)
        return cc

    def get_index_keys_dict(self):
        cc = self.get_index_keys()
        dc = dict()
        for c in cc:
            dc[c.model_k] = c
        return dc

    def get_relationship_with_model(self, model):
        if not self.relationships:
            return None
        result = None
        for k in self.relationships:
            c = getattr(self.cls, k)
            c.validate()
            if c.ref_model == model:
                if result is not None:
                    return True
                result = c
                break
        return result

    def make_relationship_with_model(self, model, virtual=False, on_delete=None):
        ref_pk = model.__meta__.get_primary_key()
        if len(ref_pk) > 1:
            raise OrmParameterError(
                "OrmModel '%s' has complex primary key and cannot be automatically mapped to the"
                " OrmModel '%s' using relationship!" % (model.__name__, self.cls.__name__)
            )
        pk = ref_pk[0]
        pk_k = pk.model_k
        attr_cls = Relationship if not virtual else VirtualRelationship
        on_delete = on_delete or FK_ONDELETE_SET_NULL
        c = attr_cls(model, on_delete=on_delete)
        k = "%s_%s" % (model.__name__.lower(), pk_k)
        if hasattr(self.cls, k):
            k = "%s_" % k
        if hasattr(self.cls, k):
            k_ = k
            i = 2
            while hasattr(self.cls, k):
                k = "%s_%i" % (k_, i)
                i += 1
        setattr(self.cls, k, c)
        c.validate()
        return self.get_relationship_with_model(model)

    def attrs_on_before_write(self, instance):
        attrs = self.get_data_attributes()
        for attr in attrs:
            attr.on_before_write(instance)

    def attrs_on_after_write(self, instance):
        attrs = self.get_data_attributes()
        for attr in attrs:
            attr.on_after_write(instance)

    def attrs_on_before_delete(self, instance, hard=None):
        attrs = self.get_data_attributes()
        for attr in attrs:
            attr.on_before_delete(instance, hard)

    def attrs_on_after_delete(self, instance, hard=None):
        attrs = self.get_data_attributes()
        for attr in attrs:
            attr.on_after_delete(instance, hard)


