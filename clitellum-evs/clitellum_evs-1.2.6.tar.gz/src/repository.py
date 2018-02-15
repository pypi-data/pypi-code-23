import pymongo

class EvsRepository(object):
    '''
    Repositorio de eventos
    '''

    def __init__(self, database, collection_name):
        self._database = database
        self._collection_name = collection_name
        self._entity_col = self._database.get_collection(self._collection_name + '_entity')
        self._applied_col = self._database.get_collection(self._collection_name + '_applied')
        self._rejected_col = self._database.get_collection(self._collection_name + '_rejected')
        self._events_col = self._database.get_collection(self._collection_name + '_events')

    def get_entity(self, query):
        '''
        Devuelve la entidad segun la query especificada
        '''
        return self._entity_col.find_one(query)

    def get_entity_by_id(self, entity_id):
        '''
        Devuelve la entidad por el identificador especificado
        '''
        return self._entity_col.find_one({"_id" : entity_id})


    def get_events(self, entity_id):
        '''
        Devuelve los eventos asociados a la entidad especificada
        '''
        return self._events_col.find({'entity_id': entity_id}) \
            .sort("version", pymongo.ASCENDING)

    def save_event(self, event, entity_id):
        '''
        Guarda el evento de la entidad especificada
        '''
        event_db = self._create_event_db(event, entity_id)
        self._events_col.update({'_id': event.get_id()}, event_db, upsert=True)

    def save_applied_event(self, event, entity_id):
        '''
        Guarda los eventos aplicados de la entidad
        '''
        event_db = self._create_event_db(event, entity_id)
        self._applied_col.update({'_id': event.get_id()}, event_db, upsert=True)
        self._events_col.remove({'_id': event.get_id()})

    def save_rejected_event(self, event, entity_id):
        '''
        Guarda los eventos rechazados de la entidad
        '''
        event_db = self._create_event_db(event, entity_id)
        self._rejected_col.update({'_id': event.get_id()}, event_db, upsert=True)
        self._events_col.remove({'_id': event.get_id()})

    def _create_event_db(self, event, entity_id):
        event_db = {}
        if not event.get_id() is None:
            event_db['_id'] = event.get_id()
        event_db['event'] = event.to_json()
        event_db['entity_id'] = entity_id
        event_db['version'] = event.get_version()
        event_db['_t'] = {"module": event.__module__,
                          "name": event.__class__.__name__}
        return event_db

    def save_entity(self, entity_id, entity, state, version):
        entity_db = {}
        entity_db['snapshot'] = entity
        entity_db['state'] = state
        entity_db['version'] = version
        self._entity_col.update({'_id' : entity_id}, \
                                             entity_db, upsert=True)

