import datetime
from pc23 import metaclass, xrange
from .meta import OrmModelMeta
from ..attributes.base import OrmComparatorMixin, DataAttributeAbstract, AttributeAbstract, ColumnAttributeAbstract
from ..values.base import wrap_value, AttributeValueVirtual, AttributeValueNull, AttributeValueAbstract
from ..attributes.relationships import ForeignAttr, RelatedToOneAbstract, RelatedToManyAbstract, ManyToMany, OneToMany
from ..funcs import DbFunctionAbstract, RequestTableBelongedColumn
from ..exceptions import OrmModelDeclarationError, OrmInstanceMustBeWritten, OrmParameterError
from ..results import OrmRelatedObjectNotAssigned, OrmResultOneToMany, OrmModelUpdateAction, OrmResultManyToMany
from ..manage import manager
from ..logs import OrmJournal


class OrmModelAbstract(object):
    def __new__(cls, *args, **kwargs):
        instance = super(OrmModelAbstract, cls).__new__(cls, *args)
        instance.__session__ = None
        instance.__existing__ = False
        instance.__parent__ = None
        instance.__m2m__ = set()
        instance.__changes__ = dict()
        instance.__triggers__ = True
        instance.__attributes__ = dict()
        instance.__loadedkeys__ = list()
        instance.log = OrmJournal(cls, instance)
        return instance

    @property
    def __modified__(self):
        """ Returns True if Model's instance been modified (and need to be written to the database to
        save changed), and False if nothing been changed or all changes been cancelled by setting their
        values to the original ones. """
        return bool(self.__changes__)

    def __setattrvalue__(self, key, value):
        """ Sets the value for the Model instance's attribute. This method uses logics of the corresponding
        attibute to store given value, processing the value via attribute's methods and resulting end-point
        one may differ from the origial given. """
        if key not in self.__attributes__ and not hasattr(self.__class__, key):
            raise AttributeError(str(key))
        c, model = self.__attributes__[key] \
            if key in self.__attributes__ \
            else getattr(self.__class__, key), self.__class__
        if not isinstance(c, (DataAttributeAbstract, DbFunctionAbstract)):
            super(OrmModelAbstract, self).__setattr__(key, value)
            return
        value_new = wrap_value(model, self, c, key, value)
        value_old = super(OrmModelAbstract, self).__getattribute__(key)
        if not isinstance(value_old, OrmComparatorMixin) and value_old == value_new:
            return
        super(OrmModelAbstract, self).__setattr__(key, value_new)

    def __setattrabs__(self, key, value):
        """ Sets the instance's attribute to the given value, bypassing any Model attribute's logics.
        @key:               The name of the attribute to set to;
        @value:             The value to set for the instance's attribute;
        """
        super(OrmModelAbstract, self).__setattr__(key, value)

    def __getforwrite__(self, key, session):
        """ Returns a value which can be passed to the database connector library as value for
        write (INSERT or UPDATE). """
        value = self.__getattribute__(key)
        if isinstance(value, AttributeValueNull):
            value = None
        elif isinstance(value, AttributeValueVirtual):
            value = value.dbvalue if hasattr(value, 'dbvalue') else value.value
        c = getattr(self.__class__, key, None)
        if isinstance(c, ColumnAttributeAbstract):
            return c.represent_for_write(value, session)
        return value

    def __initialize_from__(self, **kwargs):
        """ Initializes this instance's attributes from initial data defined for the Model. Using
        when migrating database schema in case when table creates first time. """
        triggers_enabled = self.__triggers__
        self.__triggers__ = False
        for k in kwargs:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = getattr(self.__class__, k, None)
            if not c:
                setattr(self, k, kwargs[k])
                continue
            value = kwargs[k]
            if isinstance(value, (list, tuple)) and not getattr(c, 'enumerable_value', False):
                childs = getattr(self, k)
                if not isinstance(childs, (OrmResultOneToMany, OrmResultManyToMany)):
                    raise OrmModelDeclarationError(
                        "__initial__ value declared as an array must point to the ..ToMany relationship!"
                    )
                if isinstance(childs, OrmResultManyToMany):
                    continue
                for ci in value:
                    if not isinstance(ci, dict):
                        raise OrmParameterError(
                            "__initial__ values must be a type of list of dicts for instance itself and child ones!"
                        )
                    childs.add(**ci)
                continue
            setattr(self, k, value)
        self.__triggers__ = triggers_enabled
        self.__afterload__()

    def __load__(self, **kwargs):
        """ Loads initial values, loaded from the database by SELECT, to the Model's instance. """
        triggers_enabled = self.__triggers__
        self.__triggers__ = False
        textual = kwargs.pop('__textual__', False)
        for k in kwargs:
            d = kwargs[k]
            value = d[0] if isinstance(d, (list, tuple)) else d
            c = d[1] \
                if isinstance(d, (list, tuple)) and len(d) > 1 \
                else (self.__attributes__[k] if k in self.__attributes__ else getattr(self.__class__, k))
            model = d[2] \
                if isinstance(d, (list, tuple)) and len(d) > 2 \
                else (self.__class__ if CompositeOrmModel not in self.__class__.mro() else None)
            # value = wrap_value(model, self, c, k, value, textual) if model is not None else value
            value = wrap_value(model, self, c, k, value, textual)
            # print("%s: %r (%s) = %r" % (k, c, model, value))
            self.__setattr__(k, value, on_instance_loaded=True)
            if k not in self.__attributes__ and model is not None:
                self.__attributes__[k] = c, model
            if k not in self.__loadedkeys__:
                self.__loadedkeys__.append(k)
        self.__triggers__ = triggers_enabled
        self.__afterload__()

    def __afterload__(self):
        """ Called after instance been created and all values been loaded. """
        triggers_enabled = self.__triggers__
        self.__triggers__ = False
        attrs = self.__attributes__
        for k in attrs:
            c = attrs[k][0]
            c.on_instance_load(self)
        self.__triggers__ = triggers_enabled

    def __check_modified__(self, key, new_value, *args):
        """ Verifies was the attribute changed or not by testing given values, comparing 'new_value' with
        the original one (original means value which been loaded from the database or been set at a time
        of instance creating). The original value may be proposed as last optional argument (the first
        argument of *args).
        This method returns nothing, but handles instance's __changed__ dict, adding a record about changed
        attribute to it if given (by name via 'key' argument) attribute been changed, and deleting a
        corresponding record if the original value of the attribute and new one - are same.
        @key:                   The name of the Model's attribute to verify to;
        @new_value:             The new value which is about to be set to the attribute at this time;
        @*args:                 (Optional) if given - the first argument of 'args' will be used as old
                                value instead of reading the actual value from the instance; otherwise
                                old value (to compare with) will be readen from the instance.
        """
        original_value = self.__changes__[key][0] \
            if key in self.__changes__ \
            else (args[0] if args else self.__getattribute__(key))
        new_value = new_value if not isinstance(new_value, AttributeValueNull) else None
        original_value = original_value if not isinstance(original_value, AttributeValueNull) else None
        if isinstance(new_value, AttributeValueAbstract):
            new_value = new_value.value
        if isinstance(original_value, AttributeValueAbstract):
            original_value = original_value.value
        is_changed = new_value != original_value
        if is_changed:
            self.__changes__[key] = (original_value, new_value)
        elif key in self.__changes__:
            del (self.__changes__[key])
        meta = getattr(self.__class__, '__meta__', None)
        if meta is not None and is_changed and getattr(meta, 'on_change', None) is not None:
            meta.on_change(self)

    def __set_modified__(self, key, old_value, new_value):
        """ Force set the record that attribute with given name been changed, not
        testing this fact.
        @key:                   The name of the attribute;
        @old_value:             Old value of the attribute;
        @new_value:             New value of the attribute;
        """
        self.__changes__[key] = (old_value, new_value)

    def __reset_modified__(self, key):
        """ Force remove the record (if any set before) that attribute with given name been changed,
        not testing that fact. Even if attribute's value been changed, the instance will not know
        about it any more. """
        if key not in self.__changes__:
            return
        del(self.__changes__[key])

    def __getattrabs__(self, key):
        """ Returns raw value of the instance's attribute, bypassing any attribute logics. """
        return super(OrmModelAbstract, self).__getattribute__(key)

    def __setattr__(self, key, value, on_instance_loaded=False):
        if key.startswith('__') and key.endswith('__'):
            super(OrmModelAbstract, self).__setattr__(key, value)
            return value
        if key not in dir(self.__class__) and key not in self.__attributes__:
            super(OrmModelAbstract, self).__setattr__(key, value)
            return value
        c = self.__attributes__[key][0] if key in self.__attributes__ else getattr(self.__class__, key)
        if isinstance(c, RequestTableBelongedColumn):
            c = getattr(self.__class__, key, None) or c
        if isinstance(c, AttributeAbstract) and c.setter is not None:
            original_value_ = self.__getattribute__(key)
            value_ = c.setter(self, key, value, bool(on_instance_loaded))
            if self.__triggers__:
                self.__check_modified__(key, value_, original_value_)
                c.call_on_change(self, key, value_)
            return value_
        iv = self.__getattrabs__(key)
        if isinstance(iv, AttributeValueVirtual):
            value_ = iv.set_value(self, key, value)
            if self.__triggers__:
                if iv.check_modified is not False:
                    if isinstance(value_, (list, tuple)):
                        self.__check_modified__(key, *value_)
                    else:
                        self.__check_modified__(key, value_)
                if isinstance(c, AttributeAbstract):
                    c.call_on_change(self, key, value_)
            return value
        if isinstance(c, DataAttributeAbstract):
            if self.__triggers__:
                value = c.verify(value)
                self.__check_modified__(key, value)
            self.__setattrvalue__(key, value)
            if self.__triggers__:
                c.call_on_change(self, key, value)
            return value
        super(OrmModelAbstract, self).__setattr__(key, value)
        if self.__triggers__ and isinstance(c, AttributeAbstract):
            c.call_on_change(self, key, value)
        return value

    def __getattribute__(self, key):
        if isinstance(key, str) and key.startswith('__') and key.endswith('__'):
            return super(OrmModelAbstract, self).__getattribute__(key)
        if key not in dir(self.__class__) and key not in self.__attributes__:
            return super(OrmModelAbstract, self).__getattribute__(key)
        c = self.__attributes__[key][0] if key in self.__attributes__ else getattr(self.__class__, key)
        if isinstance(c, AttributeAbstract):
            c.validate()
        if isinstance(c, AttributeAbstract) and c.getter is not None:
            return c.getter(self, key)
        value = super(OrmModelAbstract, self).__getattribute__(key)
        if isinstance(value, AttributeValueVirtual):
            value = value.get_value()
        if isinstance(value, OrmRelatedObjectNotAssigned):
            value.__parent_k__ = key
        return value


@metaclass(OrmModelMeta)
class OrmModel(OrmModelAbstract):
    def __new__(cls, *args, **kwargs):
        """ Overrides default __new__ method of the Model's class, executing some additional
        actions in addition to default ones. """
        instance = super(OrmModel, cls).__new__(cls, *args)
        attr_keys = dir(cls)
        for k in attr_keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = getattr(cls, k)
            if isinstance(c, AttributeAbstract):
                c.initialize(instance, k)
                if c.on_new is not None:
                    c.on_new(instance, k)
                continue
        if kwargs:
            for k in kwargs:
                if k.startswith('__') and k.endswith('__'):
                    continue
                instance.__load__(**kwargs)
        if cls.__meta__.on_instance_create is not None:
            cls.__meta__.on_instance_create(instance)
        return instance

    @property
    def __caption__(self):
        """ Returns caption of this Model's instance, if any caption attribute is defined. Returns
        an empty string if no caption attributes defined. """
        k_caption = self.__class__.__meta__.caption_key
        if k_caption is not None:
            return str(getattr(self, k_caption))
        return ""

    def __repr__(self):
        k_caption = self.__class__.__meta__.caption_key
        if k_caption is not None:
            return "%s(%r)" % (self.__class__.__name__, getattr(self, k_caption))
        return super(OrmModel, self).__repr__()

    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def __afterload__(self):
        if self.__class__.__meta__.on_instance_loaded is not None:
            self.__class__.__meta__.on_instance_loaded(self)
        triggers_enabled = self.__triggers__
        self.__triggers__ = False
        attrs = self.__class__.__meta__.get_attributes()
        for c in attrs:
            c.on_instance_load(self)
        self.__triggers__ = triggers_enabled

    @property
    def dict(self):
        return self.__dictpair__

    @property
    def __dictpair__(self):
        k_caption = self.__class__.__meta__.caption_key
        if not k_caption:
            raise OrmModelDeclarationError(
                "Cannot convert the OrmModel's object instance to dict-pair (key and value) because OrmModel has"
                " no caption key defined. Programmer may use 'CaptionString' attribute type or 'is_caption_key'"
                " parameter to identify - which attribute to use as caption!"
            )
        k_value = self.__class__.__meta__.value_key
        if not k_value and len(self.__class__.__meta__.primary_key) > 1:
            raise OrmModelDeclarationError(
                "Cannot convert the OrmModel's object instance to dict-pair (key and value) because OrmModel has"
                " no value key defined and the primary key for this OrmModel is complex (only one column can"
                " be used as value key). By default, simple primary key is used as value key, or programmer"
                " must define a single column as value key by him(her)self!"
            )
        elif not k_value:
            k_value = self.__class__.__meta__.primary_key[0]
        return self.__getattribute__(k_value), self.__getattribute__(k_caption)

    @classmethod
    def as_(cls, name):
        """ Returns this Model formatted to be named Model as 'name'. """
        return OrmModelAliased(cls, name)

    @classmethod
    def get(cls, *args, **kwargs):
        from ..request import OrmSelectRequest
        return OrmSelectRequest(cls, *args, **kwargs).go()

    @classmethod
    def set(cls, session=None, **kwargs):
        return OrmModelUpdateAction(model=cls, session=session, values=kwargs)

    def describe(self, virtual=True, foreign=False, recursive=False):
        keys = self.__class__.__meta__.get_attributes_keys()
        p = list()
        p.append(self.__repr__())
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = self.__attributes__.get(k, None) or getattr(self.__class__, k, None)
            if isinstance(c, (list, tuple)):
                c = c[0]
            if not c:
                continue
            if not isinstance(c, AttributeAbstract):
                continue
            if isinstance(c, ForeignAttr) and not foreign:
                p.append("    %15s = (Foreign(%s.%s))" % (k, c.related_k, c.referenced_k))
                continue
            if isinstance(c, DataAttributeAbstract):
                if not virtual and isinstance(c, AttributeValueVirtual):
                    p.append("    %15s = (Virtual)" % k)
                    continue
                p.append("    %15s = \"%r\" (%s)" % (k, getattr(self, k), c.__class__.__name__))
                continue
            if isinstance(c, RelatedToOneAbstract):
                p.append("    %15s = (...ToOne relationship)" % k)
                continue
            if isinstance(c, RelatedToManyAbstract):
                p.append("    %15s = (...ToMany relationship)" % k)
                continue
        return "\n".join(p)

    def write(self, force=False, all_attrs=False, session=None, attrs=None, initial=False):
        from ..request import OrmInsertRequest, OrmUpdateRequest
        if initial:
            all_attrs = True
        rq_session = session or self.__session__ or manager.get_session(instance=self)
        setattr(self, '__session__', rq_session)
        if self.__class__.__meta__.on_before_write is not None \
                and self.__class__.__meta__.on_before_write(self) is False:
            return
        if self.__parent__ is not None:
            parent_instance, relation_c = self.__parent__
            for x in xrange(len(relation_c.columns)):
                instance_k = relation_c.columns[x]
                parent_k = relation_c.ref_columns[x]
                if relation_c.ref_model == self.__class__:
                    instance_k, parent_k = parent_k, instance_k
                parent_v = getattr(parent_instance, parent_k)
                setattr(self, instance_k, parent_v)
            self.log.replace_uuid(parent_instance.log.current_uuid)
        k_related = self.__class__.__meta__.get_related_loaded_keys(self)
        for k in k_related:
            c = getattr(self.__class__, k, None)
            if c is None or not isinstance(c, RelatedToManyAbstract):
                continue
            v = self.__getattribute__(k)
            if isinstance(v, OrmRelatedObjectNotAssigned):
                continue
            if not isinstance(v, OrmModel):
                continue
            if v.__existing__:
                continue
            v.write(session=rq_session, force=force)
        if force or self.__modified__ or not self.__existing__:
            self.__class__.__meta__.attrs_on_before_write(self)
            rq_cls = OrmUpdateRequest if self.__existing__ else OrmInsertRequest
            if self.__existing__ and self.__class__.__meta__.on_update is not None \
                    and self.__class__.__meta__.on_update(self) is False:
                return
            elif not self.__existing__ and self.__class__.__meta__.on_insert is not None \
                    and self.__class__.__meta__.on_insert(self) is False:
                return
            session_user = rq_session.inqure_session_user()
            if session_user and self.__class__.__meta__.author_ident and not self.__existing__:
                for c in self.__class__.__meta__.author_ident:
                    if getattr(self, c.ident_k, None) is not None:
                        continue
                    setattr(self, c.ident_k, session_user)
            if session_user and self.__class__.__meta__.performer_ident:
                for c in self.__class__.__meta__.performer_ident:
                    setattr(self, c.ident_k, session_user)
            if self.__class__.__meta__.timestamp_creation and not self.__existing__:
                for c in self.__class__.__meta__.timestamp_creation:
                    setattr(self, c.model_k, datetime.datetime.now())
            if self.__class__.__meta__.timestamp_modification:
                for c in self.__class__.__meta__.timestamp_modification:
                    setattr(self, c.model_k, datetime.datetime.now())
            rq_values = dict()
            write_all_attrs = not attrs and (all_attrs or force or not self.__existing__)
            rq_k_ = attrs \
                or (self.__class__.__meta__.get_keys_for_write() if write_all_attrs else self.__changes__.keys())
            rq_k = list()
            for k in rq_k_:
                if not hasattr(self.__class__, k):
                    continue
                c = getattr(self.__class__, k)
                c_attributes_ = getattr(c, 'attributes', None)
                if c_attributes_ is not None and isinstance(c_attributes_, (list, tuple)):
                    rq_k.extend(c_attributes_)
                if not isinstance(c, ColumnAttributeAbstract):
                    continue
                rq_k.append(k)
            for k in rq_k:
                c = getattr(self.__class__, k)
                v = self.__getforwrite__(k, rq_session)
                rq_values[c] = v
            if rq_values:
                rq = rq_cls(self.__class__, values=rq_values, with_deleted=True, session=rq_session)
                if self.__existing__:
                    w = list()
                    pk = self.__class__.__meta__.primary_key
                    for k in pk:
                        v = self.__getforwrite__(k, rq_session)
                        c = getattr(self.__class__, k)
                        w.append(c == v)
                    rq.where(*w)
                rq.go()
            else:
                rq = False
            # rq_session = rq.session
            k_autoincrement = self.__class__.__meta__.auto_increment
            if not self.__existing__ \
                    and k_autoincrement is not None \
                    and not self.__getattribute__(k_autoincrement)\
                    and rq is not False:
                self.__setattrabs__(k_autoincrement, rq.inserted_id)
            self.__setattrabs__('__session__', rq_session)
            self.log.write_submition()
            self.__setattrabs__('__changes__', dict())
            self.__setattrabs__('__existing__', True)
            vkeys = self.__class__.__meta__.get_virtualkeys_for_write(self)
            for k in vkeys:
                c = getattr(self.__class__, k)
                c.write(self, k)
            self.__class__.__meta__.attrs_on_after_write(self)
            if self.__class__.__meta__.on_after_write is not None:
                self.__class__.__meta__.on_after_write(self)
        for k in k_related:
            c = getattr(self.__class__, k, None)
            if c is not None and isinstance(c, ManyToMany) and initial:
                continue
            v = self.__getattribute__(k)
            if not hasattr(v, 'write'):
                continue
            if v is self:
                continue
            if isinstance(v, OrmRelatedObjectNotAssigned):
                continue
            v.write(session=rq_session, force=force)
        self.log.new_uuid()

    def delete(self, session=None, hard_delete=False):
        """ Deletes this Model's instance from the corresponding database table. If Model has been
        defined with soft-deletion (by defining corresponding attribute) - by default, the record
        from the database not deletes, but soft-deletion flag it set instead. This behavior may be
        changed by setting 'hard_delete' optional argument to True to override soft-deletion and
        actually delete corresponding record from the database table. """
        from ..request import OrmDeleteRequest
        if not self.__existing__:
            raise OrmInstanceMustBeWritten(
                "Cannot delete OrmModel's object instance because it is not written to the database yet!"
            )
        if self.__parent__:
            related = self.__parent__[0].__meta__.get_related_using_fk(self.__parent__[1])
            for c in related:
                if isinstance(c, RelatedToOneAbstract):
                    cv = self.__parent__[0].__getattrabs__(c.model_k)
                    cv.delete()
                    # cv.reset()
                    # cv.pretend_loaded()
                elif isinstance(c, OneToMany):
                    cv = getattr(self.__parent__[0], c.model_k)
                    cv.__detach__(self)
        if self.__m2m__:
            for m2m in set(self.__m2m__):
                m2m.delete(self)
        rq_session = session or self.__session__ or manager.get_session(instance=self)
        setattr(self, '__session__', rq_session)
        hard_deletion = self.__class__.__meta__.soft_delete is None or hard_delete
        self.__class__.__meta__.attrs_on_before_delete(self, hard_deletion)
        if self.__class__.__meta__.on_before_delete is not None \
                and self.__class__.__meta__.on_before_delete(self, hard_deletion) is False:
            return
        w = list()
        pk = self.__class__.__meta__.primary_key
        for k in pk:
            v = self.__getforwrite__(k, rq_session)
            c = getattr(self.__class__, k)
            w.append(c == v)
        OrmDeleteRequest(self.__class__, session=rq_session, hard_delete=hard_delete).where(*w).go()
        self.log.write_deletion()
        self.__class__.__meta__.attrs_on_after_delete(self, hard_deletion)
        if self.__class__.__meta__.on_after_delete is not None:
            self.__class__.__meta__.on_after_delete(self, hard_deletion)

    @classmethod
    def find(cls, what, **kwargs):
        """ Searching for given 'what' over records in the database of this Model. Searching will be
        done by selecting from the corresponding database table(s) filtering by Model's attributes which
        has been defined with 'findable=True' option. Not any attribute can be used in search query,
        depending on its (attribute's) type.
        @what:                  Textual phrase which search for;
        @returns:               Corresponding OrmRequest, which may be ran using 'go()' method or any
                                other corresponding one, or clarified before.
        """
        from ..request import OrmSearchRequest
        return OrmSearchRequest(cls, what, **kwargs)

    @property
    def __pk__(self):
        """ Returns a dict of attributes' keys (which constitude the primary key of this Model), and
        their corresponding values. """
        pk = self.__class__.__meta__.get_primary_key()
        r = dict()
        for c in pk:
            r[c.model_k] = getattr(self, c.model_k)
        return r


class OrmModelAliased(object):
    """ Overrider class used to name given Model with custom textual name in SELECTing request.
    The instance of this class returned by 'Model.as_()' method.
    """
    def __init__(self, model, alias):
        self.model = model
        self.alias = alias

    def __repr__(self):
        return "AlisedSource(%s AS '%s')" % (self.model.__name__, self.alias)


class CompositeOrmModel(OrmModelAbstract):
    """ Class which used to generate results of complex queries, when single Model cannot be used
    as source for results of the query. Usual case - when querying from the database only limited
    set of attributes (even from one Model) or joining other Models.
    """
    def describe(self, virtual=True, foreign=False, recursive=False):
        keys = self.__loadedkeys__
        p = list()
        p.append("<Complex result instance>")
        for k in keys:
            if k.startswith('__') and k.endswith('__'):
                continue
            c = self.__attributes__.get(k, None) or getattr(self.__class__, k, None)
            if isinstance(c, (list, tuple)):
                c = c[0]
            # if not c:
            #     continue
            # if not isinstance(c, AttributeAbstract):
            #     continue
            if isinstance(c, ForeignAttr) and not foreign:
                p.append("    %15s = (Foreign(%s.%s))" % (k, c.related_k, c.referenced_k))
                continue
            if isinstance(c, DataAttributeAbstract):
                if not virtual and isinstance(c, AttributeValueVirtual):
                    p.append("    %15s = (Virtual)" % k)
                    continue
                p.append("    %15s = \"%r\" (%s)" % (k, getattr(self, k), c.__class__.__name__))
                continue
            if isinstance(c, RelatedToOneAbstract):
                p.append("    %15s = (...ToOne relationship)" % k)
                continue
            if isinstance(c, RelatedToManyAbstract):
                p.append("    %15s = (...ToMany relationship)" % k)
                continue
            p.append("    %15s = %r" % (k, getattr(self, k)))
        return "\n".join(p)


