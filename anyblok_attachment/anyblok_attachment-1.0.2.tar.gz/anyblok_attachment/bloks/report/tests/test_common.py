# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import BlokTestCase
from anyblok_attachment.bloks.report.common import format_path
from anyblok_attachment.bloks.report.exceptions import PathException
from anyblok.blok import BlokManager
import os


class TestReportCommon(BlokTestCase):

    def get_absolute_path(self):
        return os.path.join(
            BlokManager.getPath('report'), 'tests', 'test_common.py')

    def test_format_path_without_module(self):
        self.assertEqual(
            format_path(self.get_absolute_path()),
            self.get_absolute_path()
        )

    def test_format_path_with_module(self):
        self.assertEqual(
            format_path('report#=#tests/test_common.py'),
            self.get_absolute_path()
        )

    def test_format_path_with_invalid_path(self):
        with self.assertRaises(PathException):
            format_path('report#=#wrong/path')
