from open_publishing.core.enums import ValueStatus, FieldKind
from open_publishing.core import Field

class DatabaseObjectsList(Field):
    _database_object_type = None
    def __init__(self,
                 database_object,
                 aspect,
                 list_locator):
        super(DatabaseObjectsList, self).__init__(database_object=database_object,
                                                  aspect=aspect,
                                                  kind=FieldKind.regular)
        
        self._list_locator = list_locator
        self._objects = {}
        self._ids = []

    @property
    def value(self):
        if self._status is ValueStatus.none:
            raise RuntimeError('Accessing to field which is not set')
        else :
            return self
        
    def hard_set(self,
                 value):
        raise NotImplementedError('Is not supported at the moment') #TODO: Shall we support it?

    def gjp(self,
            gjp):
        pass #Nothing to do here

    def flush(self):
        if self._status is not ValueStatus.none:
            for obj in list(self._objects.values()):
                obj.flush()

    def update(self,
               gjp):
        guids = self._master_object(gjp)
        for fname in self._list_locator.split('.'):
            if fname in guids:
                guids = guids[fname]
            else :
                guids = None
                break
        if guids is not None:
            to_remove_ids = self._ids[:]
            for guid in guids:
                obj_id = self._database_object_type.id_from_guid(guid)
                
                if obj_id in to_remove_ids:
                    to_remove_ids.remove(obj_id)
                if obj_id not in self._objects:
                    self._create_object(guid, gjp)

            for obj_id in to_remove_ids:
                self._objects.pop(obj_id)
                self._ids.remove(obj_id)
                
            self._status = ValueStatus.soft

    def _create_object(self,
                       guid,
                       gjp):
        obj_id = self._database_object_type.id_from_guid(guid)
        self._objects[obj_id] = self._database_object_type(self._database_object._context,
                                                           obj_id)
        self._objects[obj_id]._update(gjp)
        self._ids.append(obj_id)

    def __len__(self):
        return len(self._ids)

    def __getitem__(self, key):
        return self._get_by_ids(self._ids[key])

    def _get_by_ids(self, ids):
        if isinstance(ids, list):
            return [self._objects[obj_id] for obj_id in ids]
        else :
            return self._objects[ids]

    def __setitem__(self, key, value):
        raise NotImplementedError('Is not supported at the moment') #TODO: Shall we support it?

    def __delitem__(self, key):
        self._remove_by_ids(self._ids[key])

    def _remove_by_ids(self, ids):
        if not isinstance(ids, list):
            ids = [ids]
        for obj_id in ids:
            self._database_object._context.gjp.delete(self._database_object_type._object_class,
                                                      obj_id)
            self._objects.pop(obj_id)
            self._ids.remove(obj_id)
        
    def __iter__(self):
        return iter(self._get_by_ids(self._ids))

    def remove(self,
               index):
        del self[index]
