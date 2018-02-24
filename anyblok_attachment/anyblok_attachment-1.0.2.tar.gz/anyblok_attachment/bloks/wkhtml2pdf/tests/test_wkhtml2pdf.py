# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import BlokTestCase
from sqlalchemy.exc import IntegrityError


class TestWkHtml2Pdf(BlokTestCase):

    def test_ok(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')
        self.registry.Attachment.WkHtml2Pdf.insert(label="Test", page=page)

    def test_wrong_margin_bottom(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')
        with self.assertRaises(IntegrityError):
            self.registry.Attachment.WkHtml2Pdf.insert(
                label="Test", page=page, margin_bottom=-1)

    def test_wrong_margin_left(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')
        with self.assertRaises(IntegrityError):
            self.registry.Attachment.WkHtml2Pdf.insert(
                label="Test", page=page, margin_left=-1)

    def test_wrong_margin_right(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')
        with self.assertRaises(IntegrityError):
            self.registry.Attachment.WkHtml2Pdf.insert(
                label="Test", page=page, margin_right=-1)

    def test_wrong_margin_top(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')
        with self.assertRaises(IntegrityError):
            self.registry.Attachment.WkHtml2Pdf.insert(
                label="Test", page=page, margin_top=-1)

    def test_wrong_javascript_delay(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')
        with self.assertRaises(IntegrityError):
            self.registry.Attachment.WkHtml2Pdf.insert(
                label="Test", page=page, javascript_delay=-1)

    def test_options_from_self(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')
        wkhtml2pdf = self.registry.Attachment.WkHtml2Pdf.insert(
            label="Test", page=page)
        self.assertEqual(
            wkhtml2pdf.options_from_self(),
            [
                '--margin-bottom', '10',
                '--margin-right', '10',
                '--margin-left', '10',
                '--margin-top', '10',
                '--orientation', 'Portrait',
                '--encoding', 'utf-8',
                '--javascript-delay', '200',
                '--load-error-handling', 'abort',
                '--load-media-error-handling', 'abort',
                '--copies', '1',
                '--grayscale',
                '--lowquality',
                '--page-size', 'Letter',
                '--background',
                '--images',
                '--collate',
                '--enable-javascript',
                '--enable-local-file-access',
            ]
        )

    def test_options_from_configuration(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')
        wkhtml2pdf = self.registry.Attachment.WkHtml2Pdf.insert(
            label="Test", page=page)
        self.assertEqual(
            wkhtml2pdf.options_from_configuration(),
            [
                '--quiet',
                '--no-debug-javascript',
            ]
        )

    def test_cast_html2pdf(self):
        page = self.registry.Attachment.WkHtml2Pdf.Page.insert(
            label='Test', size='Letter')
        wkhtml2pdf = self.registry.Attachment.WkHtml2Pdf.insert(
            label="Test", page=page)
        html_content = bytes(
            """
            <!doctype html>
            <html>
                <head>
                    <title>My page</title>
                </head>
                <body>
                    Hello world !!
                </body>
            </html>
            """,
            encoding='utf-8'
        )
        self.assertTrue(wkhtml2pdf.cast_html2pdf('tmp', html_content))
