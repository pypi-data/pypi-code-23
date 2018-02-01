import uuid
from collections import OrderedDict
from pc23 import xrange
from .attributes import BigAutoIncrement, AuthorIdent, CreationTimestamp, String, IndexKey
from .models.templates import OrmModelTemplate
from .manage import manager
from .exceptions import OrmManagementError, OrmLoggingError


# General event types
EVENT_UNKNOWN = 'unknown'
EVENT_CREATE = 'create'
EVENT_MODIFY = 'modify'
EVENT_DELETE = 'delete'


class OrmJournalEvent(object):
    """ A class representing a single event, which may be a complex set of changes or
    just a single record.
    """
    def __init__(self, **kwargs):
        self.event_uuid = kwargs.pop('event_uuid', None)
        self.event_user = kwargs.pop('event_user', None)
        self.event_time = kwargs.pop('event_time', None)
        self.event_type = kwargs.pop('event_type', EVENT_UNKNOWN)
        self.event_source = kwargs.pop('event_source', None)
        self.model_name = kwargs.pop('model_name', None)
        self.object_pk = kwargs.pop('object_pk', None)
        self.changes = dict()

    def __repr__(self):
        user = "unknown" if self.event_user is None else self.event_user.__caption__
        if self.event_type == EVENT_CREATE:
            return "<CREATE at %s by %s>" % (str(self.event_time), str(user))
        if self.event_type == EVENT_DELETE:
            return "<DELETE at %s by %s>" % (str(self.event_time), str(user))
        s = list()
        for k in self.changes:
            s.append("(%s=`%s`=>`%s`)" % (k, self.changes[k][0], self.changes[k][1]))
        return ("<MODIFY at %s by %s: " % (str(self.event_time), str(user))) + (", ".join(s)) + ">"


class OrmJournal(object):
    """ A general journaling class which instance generates for every declared Model (representing
    logging functionality for entire Model all over objects of this Model) and for every created
    (loaded from the database or new ones) instance, representing journal of corresponding
    single instance.
    """
    def __init__(self, model, instance=None):
        self.model = model
        self.instance = instance
        self.current_uuid = None
        self._loaded = False
        self._journal = None
        if self.instance is not None:
            self.new_uuid()

    def get_journal_model(self):
        """ Returns journal Model which stores records for this ORM Model. Returns 'None' if
        no journal is defined for this ORM Model.
        """
        if not self.model.__meta__.log:
            return None
        if self.model.__meta__.log is True:
            return manager.get_default_journal(self.model.__meta__.tag)
        if isinstance(self.model.__meta__.log, str):
            return manager.get_journal(self.model.__meta__.log, self.model.__meta__.tag)
        raise OrmManagementError("Model.__log__ must be True or (str) name of the registered journal!")

    def _ensure(self, **kwargs):
        """ Loads records from the database for this journal (for this instance). Journal caches for
        instances and queried every time for Models.
        """
        if self._loaded:
            return
        self._load(**kwargs)
        if self.instance is not None:
            self._loaded = True

    def get_instance_journal_pk(self):
        pk = self.instance.__meta__.primary_key
        wpk = list()
        for k in pk:
            wpk.append(str(getattr(self.instance, k)))
        return str("@".join(wpk))

    def _load(self, merge_with_related=True, object_pk=None, session=None):
        from .funcs import and_
        journal_model = self.get_journal_model()
        if journal_model is None or (self.instance is not None and not self.instance.__existing__):
            self._journal = None
            return
        session = manager.get_session(session=session, model=self.model, instance=self.instance)

        model_name = self.model.__name__
        object_pk = object_pk or (self.get_instance_journal_pk() if self.instance is not None else None)
        if not object_pk:
            raise OrmLoggingError("cannot get journal for non-written object or Model without 'object_pk' set!")

        where_ = list()
        where_.append(journal_model.model_name == model_name)
        where_.append(journal_model.object_pk == str(object_pk))
        request = session.select(journal_model).where(*where_)
        records = request.go()

        events = OrderedDict()
        for e in records:
            if e.event_uuid not in events:
                events[e.event_uuid] = OrmJournalEvent(
                    event_uuid=e.event_uuid,
                    event_user=e.event_user,
                    event_time=e.event_time,
                    event_type=e.event_type,
                    event_source=model_name,
                    model_name=model_name,
                    object_pk=object_pk
                )
            if e.event_type != EVENT_MODIFY:
                continue
            events[e.event_uuid].changes[e.attr_name] = (e.value_src, e.value_dst)

        foreigns = dict() if not merge_with_related else self.model.__meta__.get_foreign_attrs_by_relationships()
        if foreigns:
            for rel_c in foreigns:
                # Getting the real primary key for the related object. We have to query a database
                # for the object to do that.
                foreign_model = rel_c.foreign_model
                foreign_journal_model = foreign_model.log.get_journal_model()
                if not foreign_journal_model:
                    continue
                foreign_c = rel_c.foreign_c
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
                child = session.select(foreign_model).where(*w).limit(1).go().one()
                # If there is no child got - skipping this journal part because nothing to
                # get at all
                if child is None:
                    continue
                # Preparing to query for journal for this object
                child_pk = child.log.get_instance_journal_pk()
                foreign_model_name = child.__class__.__name__
                foreign_attrs = foreigns[rel_c]
                attrs_conformity = dict()
                attrs_names = list()
                for fc in foreign_attrs:
                    local_k = fc.model_k
                    ref_k = fc.referenced_k
                    attrs_conformity[ref_k] = local_k
                    attrs_names.append(ref_k)
                w_and = list()
                w_and.append(foreign_journal_model.model_name == foreign_model_name)
                w_and.append(foreign_journal_model.object_pk == child_pk)
                w_and.append(foreign_journal_model.attr_name.in_(attrs_names))
                w = and_(*w_and)
                # Querying for child journal
                request = session.select(foreign_journal_model).where(*w)
                foreign_records = request.go()
                # Merging with main journal, if anything got
                for e in foreign_records:
                    if e.event_type != EVENT_MODIFY:
                        continue
                    local_attr_name = attrs_conformity.get(e.attr_name, e.attr_name)
                    if e.event_uuid in events:
                        if events[e.event_uuid].event_type not in EVENT_MODIFY:
                            continue
                        if local_attr_name in events[e.event_uuid].changes:
                            continue
                    if e.event_uuid not in events:
                        events[e.event_uuid] = OrmJournalEvent(
                            event_uuid=e.event_uuid,
                            event_user=e.event_user,
                            event_time=e.event_time,
                            event_type=e.event_type,
                            event_source=e.model_name,
                            model_name=model_name,
                            object_pk=object_pk
                        )
                    events[e.event_uuid].changes[local_attr_name] = (e.value_src, e.value_dst)

        # Preparing the resulting list and sorting it by events' timestamp
        events_ = list()
        for uuid_ in events:
            events_.append(events[uuid_])
        events_ = sorted(events_, key=lambda e_: e_.event_time)
        self._journal = tuple(events_)

    def replace_uuid(self, uuid_):
        self.current_uuid = uuid_

    def new_uuid(self):
        self.current_uuid = str(uuid.uuid4())

    def get_journal(self, **kwargs):
        self._ensure(**kwargs)
        return self._journal

    def reset(self):
        self._loaded = False

    def write_submition(self, session=None):
        if self.instance is None:
            raise OrmLoggingError("cannot write journal of Model itself - can only write journal of instance!")
        journal_model = self.get_journal_model()
        if journal_model is None:
            return
        if not self.instance.__changes__ and self.instance.__existing__:
            return
        session = manager.get_session(session=session, model=self.model, instance=self.instance)
        base_kw = {
            'event_uuid': self.current_uuid,
            'event_type': EVENT_MODIFY if self.instance.__existing__ else EVENT_CREATE,
            'model_name': self.model.__name__,
            'object_pk': self.get_instance_journal_pk()
        }
        if not self.instance.__existing__:
            event = journal_model(**base_kw)
            event.__session__ = session
            event.write()
            self._loaded = False
            return
        for k in self.instance.__changes__:
            c = getattr(self.model, k, None)
            if c is None:
                continue
            src_, dst_ = c.log_repr(self.instance.__changes__[k][0], self.instance.__changes__[k][1], self.instance)
            event = journal_model(**base_kw)
            event.__session__ = session
            event.attr_name = k
            event.value_src = src_
            event.value_dst = dst_
            event.write()
        self._loaded = False

    def write_deletion(self, pk=None, session=None):
        journal_model = self.get_journal_model()
        if journal_model is None:
            return
        if pk is None and self.instance is None:
            raise OrmLoggingError("cannot log object deletion without understanding - which object!")
        pk = pk or self.get_instance_journal_pk()
        session = manager.get_session(session=session, model=self.model, instance=self.instance)
        uuid_ = str(uuid.uuid4())
        base_kw = {
            'event_uuid': uuid_,
            'event_type': EVENT_DELETE,
            'model_name': self.model.__name__,
            'object_pk': pk
        }
        event = journal_model(**base_kw)
        event.__session__ = session
        event.write()

    @property
    def events(self):
        if self.instance is None:
            raise OrmLoggingError("cannot get events for Model, call this property for instance only!")
        return self.get_journal()


class OrmJournalTemplate(OrmModelTemplate):
    id = BigAutoIncrement()
    event_uuid = String(36, nullable=False, default='')
    event_user = AuthorIdent()
    event_time = CreationTimestamp()
    event_type = String(16, nullable=False, default=EVENT_UNKNOWN)
    model_name = String(255, nullable=False)
    object_pk = String(255, nullable=False)
    attr_name = String(255, nullable=False)
    value_src = String(1023)
    value_dst = String(1023)
    idx_model_name = IndexKey(model_name, object_pk)

