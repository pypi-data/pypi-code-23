#!/usr/bin/env python
"""Base model classes for django-hotsauce"""
import logging
import schevo.mt

from notmm.dbapi.orm import RelationProxy

log = logging.getLogger(__name__)

__all__ = ('ModelManager',)

class ModelManager(object):

    model = None # Category

    def __init__(self, connection, **kwargs):
        self.kwargs = kwargs
        self.db_connection = connection
        self.objects = RelationProxy(getattr(self.db_connection, self.model))
        
    def __str__(self):
        return "<ModelManager: %s>" % self.model
    
    def save(self, commit=True):
        lock = self.db.write_lock()
        with lock:
            #if self.initialized:
            tx = self.extent.t.create(**self.kwargs)
            if commit:
                self.db.execute(tx)
                self.db._commit()
        lock.release()
        return self

