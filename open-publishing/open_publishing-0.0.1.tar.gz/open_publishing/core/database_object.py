import re
import traceback

import open_publishing.gjp

class DatabaseObject(object):
    _object_class = None
    
    def __init__(self,
                 context,
                 object_id):
        self._context = context
        self._object_id = object_id
        self._fields = {}
        self._version = None

    @classmethod
    def _create(cls,
                context,
                **kwargs):
        """Don't use it, unless you know for sure what you are doing. You've been warned"""
        res = cls(context, None)
        res._update(kwargs)
        return res
        
    @property
    def context(self):
        return self._context

    @property
    def guid(self):
        return "{0}.{1}".format(self._object_class,
                                self._object_id)

    def _gjp(self):
        gjp = {}
        for field in list(self._fields.values()):
            field.gjp(gjp)
        return gjp

    def flush(self):
        gjp = self._gjp()
        if gjp and self._object_id is None:
            res = self._context.gjp.create(self._object_class,
                                           **gjp)
            self._object_id = self.id_from_guid(res['GUID'])
            self._update(res)
        elif gjp:
            if self._version is None:
                self._fetch([])
            
            try:
                self._context.gjp.update(self._object_class,
                                         self._object_id,
                                         self._version,
                                         gjp)
            except open_publishing.gjp.ObjectHasChanged:
                self._fetch([])
                self._context.gjp.update(self._object_class,
                                         self._object_id,
                                         self._version,
                                         gjp)
        for field in list(self._fields.values()):
            field.flush()
        self._on_flush()

    def _update(self,
                gjp):
        master_obj = gjp.get(self.guid, {})
        if 'VERSION' in master_obj and self._version != master_obj['VERSION']:
            self._version = master_obj['VERSION']
            self.invalidate()
                
        for name, field in list(self._fields.items()):
            try:
                field.update(gjp)
            except Exception as e:
                raise RuntimeError("Update failed for field: '{0}'\n{1}".format(name,
                                                                                ''.join(traceback.format_exception_only(type(e), e))))
        
    
    def _fetch(self,
               aspect):
        if self._object_id is not None:
            gjp = self._context.gjp.get(self._object_class,
                                        self._object_id,
                                        fields=aspect)
            self._update(gjp)

    def invalidate(self):
        for field in list(self._fields.values()):
            field.flush()
            field.invalidate()
                

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.flush()


    @classmethod
    def id_from_guid(cls,
                     guid):
        m = re.match("^" + cls._object_class + "\.(?P<object_id>[0-9]*)$", guid)
        if m is None:
            raise ValueError("expected guid in format '{0}.1234'".format(cls._object_class))
        return  int(m.group("object_id"))        
        
    def _on_changed(self):
        pass

    def _on_flush(self):
        pass
