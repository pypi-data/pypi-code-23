"""
Entidades Event Sourcing
"""
import datetime
from clitellum_evs.rejection.engines import RejectionEventException, IgnoreRejectionEngine

EPOCH = datetime.datetime.utcfromtimestamp(0)

class DomainEvent(object):
    """
    Interface de Evento de dominio
    """

    def __init__(self, name, id, data):
        self._name = name
        self._id = id
        self._data = data
        self._version = (datetime.datetime.utcnow() - EPOCH).total_seconds() * 1000000

    def get_name(self):
        """
        Devuelve el nombre de la transicion asociada al evento
        """
        return self._name

    def get_id(self):
        return self._id

    def to_json(self):
        return self._data

    def apply(self, entity):
        """
        Realiza la aplicacion del evento sobre la entidad
        """
        pass

    def set_version(self, version):
        self._version = version

    def get_version(self):
        return self._version

    def can_apply(self, entity):
        """
        Indica si se puede aplicar el envento sobre la entidad
        """
        return True

class AggregateRoot(object):
    """
    Clase aggregate root, para la aplicacion de los eventos
    """
    def __init__(self, id, entity, state_machine, initial_state, evs_repository, snapshot_builder):
        self._state_machine = state_machine
        self._state_machine.set_state(initial_state)
        self._root = entity
        self._applied_events = []
        self._id = id
        self._version = 0
        self._rejection_engine = IgnoreRejectionEngine()
        self._evs_repository = evs_repository
        self._snapshot_builder = snapshot_builder

    def set_rejection_engine(self, engine):
        '''
        Establece el motor de rechazo
        '''
        self._rejection_engine = engine

    def get_rejection_engine(self):
        '''
        Devuelve el motor de rechazo
        '''
        return self._rejection_engine

    def add_event(self, event):
        '''
        Anade y aplica un evento al root
        '''
        self._evs_repository.save_event(event, self._id)
        self.apply_event(event)

    def apply_event(self, event):
        """
        Aplica el evento sobre la raiz
        """
        if event.get_version() < self._version:
            self._rejection_engine.reject(self, event)
            return

        if self._state_machine.transite(event.get_name()):
            if event.can_apply(self._root):
                event.apply(self._root)
                self._version = event.get_version()
                self._applied_events.append(event)
                return

        self._rejection_engine.reject(self, event)

    def apply_events(self, events):
        """
        Aplica una lista de eventos sobre la raiz
        """
        for event in events:
            try:
                self.apply_event(event)

            except RejectionEventException:
                break

    def get_applied_events(self):
        '''
        Devuelve los eventos que se han aplicado
        '''
        return self._applied_events

    def get_state(self):
        """
        Devuelve el estado de la entidad
        """
        return self._state_machine.get_state()

    def get_id(self):
        return self._id

    def get_entity(self):
        return self._root

    def get_version(self):
        return self._version

    def set_version(self, version):
        self._version = version

    def create_snapshot(self):
        '''
        Crea el snahpshot de la entidad
        '''
        self._snapshot_builder.build(self)
