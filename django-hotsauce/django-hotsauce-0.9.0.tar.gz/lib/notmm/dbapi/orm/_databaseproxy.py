#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2007-2013 Etienne Robillard
# All rights reserved.
# <LICENSE=APACHEV2>
"""Schevo database wrappers for easy integration with the XdserverBackend."""

__all__ = ['ConnectionError', 'DatabaseProxy']

#import schevo.database

        
from schevo.database import format_dbclass
from schevo.backends.durus39 import DurusBackend
#from schevo.database2 import Database

# mulithreading support
import schevo.mt

class ConnectionError(Exception):
    """Error connecting to the selected DB backend"""
    pass

class DatabaseProxy(object):
    """Creates and manages live ``Database`` objects using Proxy
    style attribute delegation. 
    
    Usage::
    
        >>> from notmm.dbapi.orm import DatabaseProxy
        >>> db = DatabaseProxy('moviereviews') # access the "moviereviews" database
        >>> article = db.Article.findone(uid=2201)
          
    """
    
    db_version = 2
    #DatabaseClass = format_dbclass[db_version] #Database
    cache = {}
    __slots__ = ['db_version', 'db_name', 'debug_schevo', 'conn', 'DatabaseClass', 'root', '_db', 'initdb']

    def __init__(self, 
        db_name, 
        db_connection_cls=DurusBackend,
        db_debug_level=0,
        sync=True
        ):
        try:
            # Initialize the connection object
            self.conn = self.cache[db_name]
        except KeyError:    
            try:
                self.conn = db_connection_cls(db_name)
                #self.conn = schevo.database.open(db_name)
                self.root = self.conn.get_root()
            except Exception as exc:
                raise ConnectionError(exc)
            else:
                self.cache[db_name] = self.conn
        else:
            if db_debug_level >= 1:
                # perform a quick sanity check
                assert 'SCHEVO' in self.root, 'Not a Schevo database or unexpected DB format: %r' % db_name
        
        setattr(self, 'db_name', str(db_name))

        self.DatabaseClass = format_dbclass[self.db_version]
        self.initdb(self.conn, sync)
    
    def initdb(self, conn, sync=True, multithread=True):


        # Finalize db; setup proper multi-threading support
        db = self.DatabaseClass(conn)
        if sync:
            db._sync()
        if multithread:
            schevo.mt.install(db)
        
        #db.pack()

        setattr(self, '_db', db)
        del db

    def __getattr__(self, name):
        lock = self._db.read_lock()
        with lock:
            try:
                attr = getattr(self._db, name)
            except AttributeError:
                raise 
        lock.release()        
        return attr

    def __repr__(self):
        return "<Database: version=%d name=%s backend=%s>" % \
            (self.db_version, self.db_name, self.DatabaseClass)

    def commit(self):
        """Invoke underlaying ``commit`` method"""
        self._db._commit()
        return None
