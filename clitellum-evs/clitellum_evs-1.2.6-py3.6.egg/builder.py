"""
Entidades Builder
"""
import sys
from clitellum_evs.repository import EvsRepository
from clitellum_evs.entities import AggregateRoot
from clitellum_evs.snapshot import SnapshotBuilder
from bson import ObjectId
from clitellum_evs.rejection.engines import IgnoreRejectionEngine, StopOnErrorRejectionEngine

class AggregateRootBuilder(object):
    """
    Aggregate Root Builder for finite state machines.
    """
    def __init__(self, evs_repository, state_machine_class):
        self._state_machine_class = state_machine_class
        self._id = None
        self._state = None
        self._query = None
        self._events = []
        self._rejection_engine = IgnoreRejectionEngine()
        self._evs_repository = evs_repository
        self._snapshot_builder = SnapshotBuilder(evs_repository)

    @classmethod
    def create(cls, database, collection_name, state_machine_class):
        """

        :param database: base de datos.
        :param collection_name: nombre de la coleccion donde reflejar los eventos.
        :param state_machine_class: nombre de la clase tipo de la maquina de estados.
        :return: src.builder.AggregateRootBuilder
        """
        repository = EvsRepository(database, collection_name)
        return AggregateRootBuilder(repository, state_machine_class)

    def set_entity(self, obj_id):
        """
        Setea el id de la entidad.
        :param obj_id: identificador de la entidad
        """
        self._id = obj_id
        return self
    
    def set_entity_from_query(self, query):
        """
        Setea el id de la entidad.
        :param id: identificador de la entidad
        """
        self._query = query
        return self

    def set_initial_state(self, state):
        """
        Setea el estado inicial
        :param state: estado
        """
        self._state = state
        return self

    def set_stop_on_rejection(self):
        '''
        Establece el motor de rechazo StopOnErrorRejection, no aplica mas eventos si uno 
        da error
        '''
        self._rejection_engine = StopOnErrorRejectionEngine()
        return self

    def set_snapshot_builder(self, builder):
        """
        Setea el snapshot_builder
        :param builder: snapshot builder
        """
        self._snapshot_builder = builder
        return self

    def add_event(self, event):
        """
        Anade un evento con version.
        :param event: evento
        """
        self._events.append(event)
        return self

    def build(self):
        """
        Hace el build de un Aggregate Root
        :return:
        """
        self._get_id()

        for event in self._events:
            self._evs_repository.save_event(event, self._id)

        entity = self._evs_repository.get_entity_by_id(self._id)
        events = self._evs_repository.get_events(self._id)
        machine = self._state_machine_class()

        if self._state is None:
            self._state = machine.get_initial_state()

        if entity is None:
            root = AggregateRoot(self._id, {}, machine, self._state, self._evs_repository, self._snapshot_builder)
        else:
            root = AggregateRoot(self._id, entity['snapshot'], machine, entity['state'], self._evs_repository, self._snapshot_builder)
            root.set_version(entity['version'])

        root.set_rejection_engine(self._rejection_engine)

        root_events = []
        for event in events:
            event_class = getattr(sys.modules[event['_t']['module']], event['_t']['name'])
            ev = event_class(event['_id'], event['event'])
            ev.set_version = event['version']
            root_events.append(ev)
        
        root.apply_events(root_events)
        return root

    def _get_id(self):
        if not self._id is None:
            return
        if self._query is None:
            self._id = ObjectId()
        ret = self._evs_repository.get_entity(self._query)
        if ret is None:
            self._id = ObjectId()
        else:
            self._id = ret['_id']


