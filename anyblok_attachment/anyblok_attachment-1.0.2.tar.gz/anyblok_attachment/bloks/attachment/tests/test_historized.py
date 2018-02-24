# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import BlokTestCase
from anyblok.bloks.anyblok_core.exceptions import (
    ForbidUpdateException, ForbidDeleteException)
from os import urandom


class TestHistorized(BlokTestCase):

    def test_query_only_history(self):
        document = self.registry.Attachment.Document.Latest.insert()
        history = self.registry.Attachment.Document.History.insert(
            uuid=document.uuid, version='other')
        self.assertIs(
            self.registry.Attachment.Document.History.query().filter_by(
                uuid=document.uuid).one(),
            history
        )

    def test_update(self):
        file_ = urandom(100)
        document = self.registry.Attachment.Document.insert(file=file_)
        document.historize_a_copy()
        with self.assertRaises(ForbidUpdateException):
            document.previous_version.data = {'other': 'data'}
            self.registry.flush()

    def test_delete(self):
        file_ = urandom(100)
        document = self.registry.Attachment.Document.insert(file=file_)
        document.historize_a_copy()
        with self.assertRaises(ForbidDeleteException):
            document.previous_version.delete()
            self.registry.flush()
