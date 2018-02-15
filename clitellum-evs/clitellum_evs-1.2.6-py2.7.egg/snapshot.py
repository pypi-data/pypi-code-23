import sys
from clitellum_evs.repository import EvsRepository
from clitellum_evs.rejection.engines import IgnoreRejectionEngine, StopOnErrorRejectionEngine

class SnapshotBuilder(object):
    """
    Creador de imagenes de una entidad en concreto.
    """
    def __init__(self, evs_repository):
        self._evs_repository = evs_repository
        self._remove_rejected_events = True


    def set_remove_rejected_events(self, remove):
        '''
        Estable si al crear el snapshot hay que eliminar los eventos que han sido rechazados
        por defecto no se eliminan de la lista de eventos.
        '''
        self._remove_rejected_events = remove
        return self

    def build(self, root):
        """
        Build
        """
        for event in root.get_applied_events():
            self._evs_repository.save_applied_event(event, root.get_id())

        if self._remove_rejected_events:
            for event in root.get_rejection_engine().get_rejected_events():
                self._evs_repository.save_rejected_event(event, root.get_id())

        self._evs_repository.save_entity(root.get_id(), root.get_entity(), \
                                        root.get_state(), root.get_version())
