# -*- coding: utf-8 -*-

"""Base APIs to handle all storage-related operations on info descriptors.

Module's content
================

"""

import os
from . import configRootDir, checkRootDir
import sqlite3


class DataLoadStoreDbError(Exception):
    """Base module's exception class, wraps database errors."""

    def __init__(self, dbError):
        """Constructor.

        :param object dbError: instance of a database exception.
        """
        self._dbError = dbError

    def __str__(self):
        """Error message."""
        return "Errore generico di database: '{}'".format(
            self._dbError.__str__())


class DescIo:
    """Base descriptors I/O class.

    For any implemented descriptor, this class shall be subclassed.
    Only :py:meth:`_initDb()` method has to be defined by any subclass.
    In case however a descriptor I/O operations have peculiar requirements,
    other class' methods may be redefined in sucbclass too.

    Actual descriptors' storage relies on a SQLite db. 1-to-1 relationship
    between descriptors and tables must hold.
    """

    #: Internal copy of :py:data:`~pisim.dataLoadStore.configRootDir`
    #: Class-level member,
    _configRootDir = configRootDir

    #: Instance of the SQLite DB connection.
    #: Class-level member.
    _conn = None

    #: List of names of classes for which at least one instance of related
    #: I/O class has been already created. In that way, db initialization part
    #: for a given descriptor type is executed only once.
    #: Class-level member.
    _initedClasses = []

    @staticmethod
    def serializeDesc(desc):
        """Serialize a dict-type descriptor.

        Descriptors used by the app are free-structured dictionaries, which
        means that there can be any number of nested dictionaries.
        To enable their procedural handling, they must be simplified,
        namely at each key a "simple" value (no dict, no list) shall
        be assigned. In other terms, descriptors need to be serialized.
        This method implement such a serialization, returning a
        serialized copy of the dictionary given in input.

        To explain what serialization means a simple example may help:

        * Input dict: {'k1': {'k2': {'k3': value}}}
        * Output dict: {'k1.k2.k3': value}

        :param dict desc: The descriptor to be serialized.
        :return: A serialized copy of the input descriptor.
        :rtype: dict
        """
        def _serialize(desc, keyPrefix=''):
            retVal = {}
            if isinstance(desc, dict):
                for k in desc:
                    kEquiv = '{}.{}'.format(keyPrefix, k) if keyPrefix else k
                    retVal.update(_serialize(desc[k], kEquiv))
            else:
                retVal[keyPrefix] = desc
            return retVal

        return _serialize(desc)

    @staticmethod
    def deserializeDesc(desc):
        """De-serialize a descriptor.

        This is the complimentary method of :py:meth:`serializeDesc`.

        :param dict desc: The descriptor to be de-serialized.
        :return: A de-serialized copy of the input descriptor.
        :rtype: dict
        """
        def _deserializeAndSet(desc, masterK, value):
            while True:
                try:
                    if '.' not in masterK:
                        desc[masterK] = value
                    else:
                        _deserializeAndSet(
                            desc[masterK.split('.')[0]],
                            masterK[masterK.find('.')+1:],
                            value)
                    break
                except KeyError:
                    desc[masterK.split('.')[0]] = {}

        retVal = {}
        for k in desc:
            _deserializeAndSet(retVal, k, desc[k])

        return retVal

    def _initDb(self):
        """Private method to carry the DB initialization out.

        This method **shall be defined by each sublcass**.
        It must carry out the creation of DB table(s) to store the
        descriptors the sub-class is intended to handle.
        """
        raise NotImplementedError

    def __init__(self, moduleName, tableDef, tableDescTranslation):
        """Constructor.

        Instance is instructed so that it knows: the DB tables where it must
        operate; the table definition (in terms of field and their types);
        the table-to-descriptor translation (and vice versa.)

        :param str moduleName: The module to which descriptors that will be
            passed to methods refer to. Internally it will be used as the name
            of the DB's table that descriptors will be stored in.
        :param str tableDef: DB's table definition. It's a string
            containing the piece of the ``CREATE TABLE`` query defining tables
            fields along with their type. In other words, such a string shall
            be something like this: ``<name> <type> <constraints>,``, repeated
            for all tables fields. This string is meant to be used only in the
            :py:meth:`_initDb` method.
        :param dict tableDescTranslation: A dictionary providing the
            translation between tables field names and descriptors serialized
            keys. Each key shall be the name of a tables field: its value
            shall be the related, serialized key of the descriptor. See
            :py:meth:`serializeDesc`.
        """
        #: Name of the module which the instance shall work on.
        #: Allocated and initialized in :py:meth:`__init__`.
        self._module = moduleName
        #: Table definition.
        #: Allocated and initialized in :py:meth:`__init__`.
        self._tableDef = tableDef
        #: Table-to-descriptor translation rule.
        #: Allocated and initialized in :py:meth:`__init__`.
        self._tableDescTranslation = tableDescTranslation

        if not DescIo._conn:
            checkRootDir()
            try:
                DescIo._conn = sqlite3.connect(
                    os.path.join(DescIo._configRootDir, 'piSimData'),
                    detect_types=sqlite3.PARSE_DECLTYPES)
                DescIo._conn.execute('PRAGMA foreign_keys = 1')
                DescIo._conn.row_factory = sqlite3.Row
            except sqlite3.Error as e:
                raise DataLoadStoreDbError(e)

        if self.__class__.__name__ not in DescIo._initedClasses:
            self._initDb()
            DescIo._initedClasses.append(self.__class__.__name__)

    def load(self, descId, deserialized=True):
        """Descriptor loading.

        :param int descId: Numeric id of the descriptor to be loaded.
            It is supposed to be taken from the descriptors list
            obtained by :py:meth:`list`.
        :param bool deserialized: Tells the method if the returned descriptor
            shall be deserialized or not.
        :return: The loaded descriptor. It's ``{}`` if load fails.
        :rtype: dict
        """
        desc = {}

        try:
            for row in DescIo._conn.execute(
                    'SELECT * FROM {} WHERE descId=?'.format(
                        self._module), (descId,)):
                for k in [_ for _ in row.keys() if _ != 'descId']:
                    try:
                        desc[self._tableDescTranslation[k]] = row[k]
                    except KeyError:
                        desc[k] = row[k]
        except sqlite3.Error as e:
            raise DataLoadStoreDbError(e)

        return (DescIo.deserializeDesc(desc) if deserialized else desc)

    def save(self, desc, serialized=False):
        """Descriptor saving.

        :param dict desc: Descrptor to be stored. In case this descriptor
            has to replace an existing one, the descriptor itself shall have
            the key ``descId``, holding the id of the row in DB table to
            be replaced. In case instead descriptor is brand new, the said key
            is not needed.
        :param bool serialized: Tells the method if the passed descriptor
            is serialized or not.
        :return: The id of the saved row in DB. It is the same as
            descriptor's ``descId`` key in case it's present.
        :rtype: int
        """
        descSer = DescIo.serializeDesc(desc) if not serialized else desc
        reverseTranslation = \
            dict(zip(self._tableDescTranslation.values(),
                     self._tableDescTranslation.keys()))

        try:
            query = 'INSERT OR REPLACE INTO {} ({}) VALUES ({})'.format(
                self._module,
                ', '.join([reverseTranslation.get(k, k) for k in descSer]),
                ', '.join(['?']*len(descSer)))
            DescIo._conn.execute(query, descSer.values())
            DescIo._conn.commit()
        except sqlite3.Error as e:
            raise DataLoadStoreDbError(e)

        crs = DescIo._conn.cursor()
        crs.execute('SELECT last_insert_rowid()')
        return crs.fetchone()[0]

    def delete(self, descId):
        """Descriptor delete.

        :param int descId: numeric id of the descriptor in DB to be removed.
        """
        try:
            self._conn.execute(
                '''DELETE FROM {} WHERE descId=?'''.format(
                    self._module), (descId, ))
            DescIo._conn.commit()
        except sqlite3.Error as e:
            raise DataLoadStoreDbError(e)

    def list(self):
        """List retrieval of stored descriptors.

        :return: A list of stored descriptors. Each item of such a list
            is a dictionary with keys ``('descId', 'name')``. For each
            stored descriptor is hence returned the row's id and its name.
        :rtype: list
        """
        try:
            return [{'descId': r['descId'], 'name': r['name']}
                    for r in DescIo._conn.execute(
                        'SELECT descId, name FROM {}'.format(self._module))]
        except sqlite3.Error as e:
            raise DataLoadStoreDbError(e)


class Model1DescIo(DescIo):
    """Intermediate class subclassed by many final descriptors I/O classes.

    This class implements the :py:meth:`_initDb` which is common
    to many descriptor DB tables.
    """

    def _initDb(self):
        try:
            DescIo._conn.execute(
                ("CREATE TABLE IF NOT EXISTS {} "
                 "(descId INTEGER PRIMARY KEY, {})").format(
                    self._module, self._tableDef.format('UNIQUE NOT NULL')))
            DescIo._conn.commit()
        except sqlite3.Error as e:
            raise DataLoadStoreDbError(e)
