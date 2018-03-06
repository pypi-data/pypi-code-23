###############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id: __init__.py 4416 2015-11-10 12:18:08Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import os
import tempfile

import pymongo

import zope.schema
from zope.publisher.browser import FileUpload
from zope.testing.loggingsupport import InstalledHandler

import m01.mongo.interfaces
import m01.mongo.testing
import m01.stub.testing
from m01.mongo.fieldproperty import MongoFieldProperty

from m01.zfs import interfaces
import m01.zfs.item


# mongo db name used for testing
TEST_DB_NAME = 'm01_zfs_testing'
TEST_COLLECTION_NAME = 'test.files'
TEST_COLLECTION_FULL_NAME = '%s.%s' % (TEST_DB_NAME, TEST_COLLECTION_NAME)


###############################################################################
#
# test helper methods
#
###############################################################################

_testClient = None

def getTestClient():
    return _testClient


def getTestDatabase():
    client = getTestClient()
    return client[TEST_DB_NAME]


def getTestCollection():
    database = getTestDatabase()
    return database[TEST_COLLECTION_NAME]


def dropTestDatabase():
    client = getTestClient()
    client.drop_database(TEST_DB_NAME)


def dropTestCollection():
    client = getTestClient()
    client[TEST_DB_NAME].drop_collection(TEST_COLLECTION_NAME)


# stub mongodb server
def setUpStubMongo(test=None):
    """Setup pymongo client as test client and setup a real empty mongodb"""
    host = 'localhost'
    port = 45017
    tz_aware = True
    sandBoxDir = os.path.join(os.path.dirname(__file__), 'sandbox')
    m01.stub.testing.startMongoServer(host, port, sandBoxDir=sandBoxDir)
    # setup pymongo.MongoClient as test client
    global _testClient
    _testClient = pymongo.MongoClient(host, port, tz_aware=tz_aware)
    logger = InstalledHandler('m01.zfs')
    test.globs['logger'] = logger


def tearDownStubMongo(test=None):
    """Tear down real mongodb"""
    # stop mongodb server
    sleep = 0.5
    m01.stub.testing.stopMongoServer(sleep)
    # reset test client
    global _testClient
    _testClient = None
    logger = test.globs['logger']
    logger.clear()
    logger.uninstall()
    # clear thread local transaction cache
    m01.mongo.clearThreadLocalCache()


###############################################################################
#
# test helper
#
###############################################################################

class FakeFieldStorage(object):
    """A fake field storage"""

    def __init__(self, upload, filename, headers):
        self.file = upload
        self.filename = filename
        self.headers = headers

def getFileUpload(txt, filename=None, headers=None):
    if filename is None:
        filename = 'test.txt'
    if headers is None:
        headers = {}
    upload = tempfile.SpooledTemporaryFile('w+b')
    upload.write(txt)
    upload.seek(0)
    fieldStorage = FakeFieldStorage(upload, filename, headers)
    return FileUpload(fieldStorage)


###############################################################################
#
# Public Base Tests
#
###############################################################################

class FileItemBaseTest(m01.mongo.testing.MongoItemBaseTest):
    """fileItem base test"""

    def test_providedBy_IFile(self):
        obj = self.makeTestObject()
        self.assert_(interfaces.IFile.providedBy(obj), True)

    def test_providedBy_IFileItem(self):
        obj = self.makeTestObject()
        self.assert_(interfaces.IFileItem.providedBy(obj), True)


###############################################################################
#
# test components
#
###############################################################################

class TestFilesCollectionMixin(object):
    """Test files collection mixin class"""

    @property
    def collection(self):
        return getTestCollection()


class ITestSchema(zope.interface.Interface):
    """Basic test schema."""

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'Title',
        default=u'',
        required=True)

    description = zope.schema.Text(
        title=u'Description',
        description=u'Description',
        default=u'',
        required=False)


class ISampleFileStorageItem(ITestSchema, interfaces.IFileStorageItem):
    """Sample storage file item interface."""

    __name__ = zope.schema.TextLine(
        title=u'Title',
        description=u'Title',
        missing_value=u'',
        default=None,
        required=True)


class SampleFileStorageItem( m01.zfs.item.FileStorageItem):
    """Sample file storage item."""

    zope.interface.implements(ISampleFileStorageItem)

    title = MongoFieldProperty(ISampleFileStorageItem['title'])
    description = MongoFieldProperty(ISampleFileStorageItem['description'])

    dumpNames = ['title', 'description']


class ISampleFileStorage(m01.mongo.interfaces.IMongoStorage):
    """Sample file storage interface."""


class SampleFileStorage(TestFilesCollectionMixin,
    m01.mongo.storage.MongoStorage):
    """Sample file storage."""

    zope.interface.implements(ISampleFileStorage)

    def __init__(self):
        pass

    def load(self, data):
        """Load data into the right mongo item."""
        return SampleFileStorageItem(data)
