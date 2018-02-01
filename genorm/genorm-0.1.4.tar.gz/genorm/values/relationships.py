from pc23 import xrange
from ..exceptions import OrmAttributeIsProtected, OrmModelClassMismatch
from ..mapper import mapper
from ..manage import manager
from .base import AttributeValueVirtual


class ValueRelatedToOne(AttributeValueVirtual):
    def delete(self):
        sz = len(self.c.foreign_c.columns)
        triggers_enabled = self.instance.__triggers__
        for x in xrange(sz):
            local_k = self.c.foreign_c.columns[x]
            setattr(self.instance, local_k, None)
        self.instance.__triggers__ = triggers_enabled
        self.reset()
        self.pretend_loaded()

    def set_value(self, instance, key, value):
        from ..results import OrmRelatedObjectNotAssigned
        self.c.validate()
        self.c.foreign_c.validate()
        if value is not None and not isinstance(value, self.c.foreign_model):
            raise OrmModelClassMismatch(
                "assigning object instance of type %s while required %s!"
                % (type(value), self.c.foreign_model.__name__)
            )
        if not getattr(value, '__existing__', True):
            value.write(session=self.instance.__session__)
        sz = len(self.c.foreign_c.columns)
        triggers_enabled = instance.__triggers__
        for x in xrange(sz):
            local_k = self.c.foreign_c.columns[x]
            if not value:
                setattr(instance, local_k, None)
                continue
            ref_k = self.c.foreign_c.ref_columns[x]
            ref_value = getattr(value, ref_k)
            setattr(instance, local_k, ref_value)
        instance.__triggers__ = triggers_enabled
        self._loaded = True
        self._value = value if value else OrmRelatedObjectNotAssigned(instance, self.c.foreign_c)

    def load(self):
        from ..results import OrmRelatedObjectNotAssigned
        self._loaded = True
        self.c.validate()
        foreign_model = self.c.foreign_model
        foreign_c = self.c.foreign_c
        session = self.instance.__session__
        if session is None:
            return OrmRelatedObjectNotAssigned(self.instance, foreign_c)
        foreign_c.validate()
        w = list()
        notnone = False
        for x in xrange(len(foreign_c.columns)):
            if foreign_c.model == self.instance.__class__:
                fc_ = getattr(foreign_model, foreign_c.ref_columns[x])
                lv_ = getattr(self.instance, foreign_c.columns[x])
            else:
                fc_ = getattr(foreign_model, foreign_c.columns[x])
                lv_ = getattr(self.instance, foreign_c.ref_columns[x])
            if lv_:
                notnone = True
            w.append(fc_ == lv_)
        child = session.select(foreign_model).where(*w).limit(1).go().first if notnone else None
        if child is None:
            return OrmRelatedObjectNotAssigned(self.instance, foreign_c)
        child.__setattrabs__('__parent__', (self.instance, foreign_c))
        return child

    def pretend_loaded(self):
        from ..results import OrmRelatedObjectNotAssigned
        super(ValueRelatedToOne, self).pretend_loaded()
        self.c.validate()
        foreign_c = self.c.foreign_c
        self._value = OrmRelatedObjectNotAssigned(self.instance, foreign_c)


class ValueRelatedToMany(AttributeValueVirtual):
    def set_value(self, instance, key, value):
        raise OrmAttributeIsProtected("the ...ToMany relationship attribute cannot be assigned to the value!")

    def load(self):
        from ..results import OrmResultOneToMany, OrmResult
        self._loaded = True
        self.c.validate()
        foreign_model = self.c.foreign_model
        foreign_c = self.c.foreign_c
        session = self.instance.__session__
        if session is None:
            r = OrmResultOneToMany(OrmResult())
            r.model = foreign_model
            r.relation_c = foreign_c
            r.parent_instance = self.instance
            return r
        foreign_c.validate()
        w = list()
        for x in xrange(len(foreign_c.columns)):
            if foreign_c.model == self.instance.__class__:
                fc_ = getattr(foreign_model, foreign_c.ref_columns[x])
                lv_ = getattr(self.instance, foreign_c.columns[x])
            else:
                fc_ = getattr(foreign_model, foreign_c.columns[x])
                lv_ = getattr(self.instance, foreign_c.ref_columns[x])
            w.append(fc_ == lv_)
        childs = session.select(foreign_model).where(*w).go()
        r = OrmResultOneToMany(childs)
        r.model = foreign_model
        r.relation_c = foreign_c
        r.parent_instance = self.instance
        for instance in r.objects:
            instance.__setattrabs__('__parent__', (self.instance, foreign_c))
        return r


class ValueManyToMany(AttributeValueVirtual):
    def __init__(self, session=None):
        super(ValueManyToMany, self).__init__()
        self.session = session

    def set_value(self, instance, key, value):
        raise OrmAttributeIsProtected("the ManyToMany relationship attribute cannot be assigned to the value!")

    def load(self):
        from ..session import OrmSessionAbstract
        from ..results import OrmResultManyToMany

        self._loaded = True
        self.c.validate()

        if not self.instance.__existing__:
            # TODO! If instance not been written yet - do an empty list!
            pass

        self.session = manager.get_session(session=self.session, instance=self.instance)
        if not isinstance(self.session, OrmSessionAbstract):
            # TODO! If instance not been written yet - do an empty list!
            pass

        local_model = self.c.model
        local_model_name = self.c.key[0] if self.c.key[0] == self.c.model.__name__ else self.c.key[1]
        ref_model_name = self.c.key[1] if self.c.key[0] == self.c.model.__name__ else self.c.key[0]
        ref_model = mapper.get_model_by_name(ref_model_name)
        join_columns = self.c.junction_model.__m2m_columns__[ref_model.__name__]
        c_columns = self.c.junction_model.__m2m_columns__[local_model.__name__]
        j_args = list()
        for jc in join_columns:
            mc = getattr(ref_model, jc.parent_model_k)
            j_args.append(jc == mc)
        w = list()
        for jc in c_columns:
            kv = self.instance.__getattrabs__(jc.parent_model_k)
            jjc = getattr(self.c.junction_model, jc.model_k)
            w.append(jjc == kv)
        dbr = self.session.select(ref_model).join(self.c.junction_model, *j_args).where(*w).get(ref_model).go()
        r = OrmResultManyToMany(dbr)
        r.parent_instance = self.instance
        r.relation_c = self.c
        r.local_model = local_model
        r.ref_model = ref_model
        r.local_model_name = local_model_name
        r.ref_model_name = ref_model_name
        r.junction_model = self.c.junction_model
        r.m2m_key = self.c.key
        return r


