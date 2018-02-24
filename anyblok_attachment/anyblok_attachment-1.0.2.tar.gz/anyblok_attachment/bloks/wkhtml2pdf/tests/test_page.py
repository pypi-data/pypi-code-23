# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import BlokTestCase
from anyblok_attachment.bloks.wkhtml2pdf.exceptions import PageValidityException
from sqlalchemy.exc import IntegrityError


class TestPage(BlokTestCase):

    def test_height(self):
        with self.assertRaises(IntegrityError):
            self.registry.Attachment.WkHtml2Pdf.Page.insert(
                label='Test', height=-1, width=10)

    def test_width(self):
        with self.assertRaises(IntegrityError):
            self.registry.Attachment.WkHtml2Pdf.Page.insert(
                label='Test', width=-1, height=10)

    def test_empty(self):
        with self.assertRaises(PageValidityException):
            self.registry.Attachment.WkHtml2Pdf.Page.insert(
                label='Test')

    def test_size(self):
        self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')

    def test_size_first_than_height_and_width(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter', height=80, width=120)
        self.assertIsNone(page.height)
        self.assertIsNone(page.width)

    def test_height_and_width(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', height=80, width=120)
        self.assertIsNotNone(page.height)
        self.assertIsNotNone(page.width)

    def test_get_options_with_size(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')
        self.assertEqual(page.get_options(), ['--page-size', 'Letter'])

    def test_get_options_with_width_and_height(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', width=120, height=80)
        self.assertEqual(page.get_options(),
                         ['--page-width', '120', '--page-height', '80'])
