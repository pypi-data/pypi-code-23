# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import BlokTestCase
from anyblok.bloks.anyblok_core.exceptions import ForbidDeleteException
from ..exceptions import ProtectedFieldException, NoFileException
from os import urandom


class TestLatest(BlokTestCase):

    def test_insert_from_document(self):
        document = self.registry.Attachment.Document.insert()
        self.assertEqual(document.type, 'latest')

    def test_insert_from_latest(self):
        document = self.registry.Attachment.Document.Latest.insert()
        self.assertEqual(document.type, 'latest')

    def test_same_version_for_two_different_document(self):
        document1 = self.registry.Attachment.Document.Latest.insert()
        document2 = self.registry.Attachment.Document.Latest.insert()
        self.assertEqual(document1.version, document2.version)
        self.assertNotEqual(document1.uuid, document2.uuid)

    def test_query_only_latest(self):
        document = self.registry.Attachment.Document.Latest.insert()
        self.registry.Attachment.Document.History.insert(uuid=document.uuid,
                                                         version='other')
        self.assertIs(
            self.registry.Attachment.Document.Latest.query().filter_by(
                uuid=document.uuid).one(),
            document
        )

    def test_create_an_history_without_file(self):
        document = self.registry.Attachment.Document.insert()
        with self.assertRaises(NoFileException):
            document.historize_a_copy()

    def test_create_an_history_with_file(self):
        file_ = urandom(100)
        document = self.registry.Attachment.Document.insert(file=file_)
        version = document.version
        self.assertTrue(document.file)
        document.historize_a_copy()
        self.assertNotEqual(document.version, version)
        self.assertIs(document.previous_version.next_version, document)
        self.assertTrue(document.file)
        self.assertTrue(document.previous_version.file)

    def test_udpate_without_file(self):
        document = self.registry.Attachment.Document.insert()
        version = document.version
        document.data = {'other': 'data'}
        self.registry.flush()
        self.assertEqual(document.version, version)
        self.assertIsNone(document.previous_version)

    def test_update_with_file(self):
        file_ = urandom(100)
        document = self.registry.Attachment.Document.insert(file=file_)
        version = document.version
        self.assertTrue(document.file)
        document.data = {'other': 'data'}
        self.registry.flush()
        self.assertNotEqual(document.version, version)
        self.assertIs(document.previous_version.next_version, document)
        self.assertFalse(document.file)
        self.assertTrue(document.previous_version.file)

    def test_delete(self):
        document = self.registry.Attachment.Document.insert()
        with self.assertRaises(ForbidDeleteException):
            document.delete()
            self.registry.flush()

    def test_versions(self):
        file_ = urandom(100)
        document = self.registry.Attachment.Document.insert(file=file_)
        document.historize_a_copy()
        self.assertEqual(
            document.previous_versions, [document.previous_version])

    def test_update_protected_fields(self):
        document = self.registry.Attachment.Document.insert()
        with self.assertRaises(ProtectedFieldException):
            document.version = 'other'
            self.registry.flush()

    def test_add_new_version_without_file(self):
        document = self.registry.Attachment.Document.insert()
        with self.assertRaises(NoFileException):
            document.add_new_version()

    def test_add_new_version_with_file(self):
        file_ = urandom(100)
        document = self.registry.Attachment.Document.insert(file=file_)
        version = document.version
        self.assertTrue(document.file)
        document.add_new_version()
        self.assertNotEqual(document.version, version)
        self.assertIs(document.previous_version.next_version, document)
        self.assertFalse(document.file)
        self.assertTrue(document.previous_version.file)
