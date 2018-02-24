# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_attachment.bloks.report.exceptions import (
    TemplateException, PathException)
from os import urandom


class TestTemplate(DBTestCase):
    blok_entry_points = ('bloks', 'test_bloks')

    def test_without_parser(self):
        registry = self.init_registry_with_bloks(['test_report_1'], None)
        with self.assertRaises(TemplateException):
            registry.Attachment.Template.MyTemplate.insert(
                parser_model="",
                template_path="report#=#common.py",
                model="Model.System.Blok"
            )

    def test_without_template(self):
        registry = self.init_registry_with_bloks(['test_report_1'], None)
        with self.assertRaises(PathException):
            registry.Attachment.Template.MyTemplate.insert(
                template_path="",
                model="Model.System.Blok"
            )

    def test_add_new_parser_type_single_table(self):
        file_ = urandom(10)
        registry = self.init_registry_with_bloks(['test_report_1'], None)
        registry.Attachment.Template.MyTemplate.file_ = file_
        template = registry.Attachment.Template.MyTemplate.insert(
            template_path="report#=#common.py",
            filename='test',
            model="Model.System.Blok"
        )
        document = registry.Attachment.Document.insert(template=template)
        get_file = document.get_file()
        wanted_file = {
            'filename': 'test',
            'file': file_,
            'filesize': len(file_),
            'contenttype': 'plain/text',
            'file_added_at': get_file['file_added_at'],
            'hash': get_file['hash']
        }
        self.assertEqual(get_file, wanted_file)
        self.assertTrue(get_file['hash'])
        self.assertTrue(get_file['file_added_at'])

    def test_add_new_parser_type_multi_table(self):
        file_ = urandom(10)
        registry = self.init_registry_with_bloks(['test_report_2'], None)
        registry.Attachment.Template.MyTemplate.file_ = file_
        template = registry.Attachment.Template.MyTemplate.insert(
            template_path="report#=#common.py",
            filename='test',
            model="Model.System.Blok"
        )
        document = registry.Attachment.Document.insert(template=template)
        get_file = document.get_file()
        wanted_file = {
            'filename': 'test',
            'file': file_,
            'filesize': len(file_),
            'contenttype': 'plain/text',
            'file_added_at': get_file['file_added_at'],
            'hash': get_file['hash']
        }
        self.assertEqual(get_file, wanted_file)
        self.assertTrue(get_file['hash'])
        self.assertTrue(get_file['file_added_at'])

    def test_add_template_with_wkhtml2pdf(self):
        file_ = urandom(10)
        registry = self.init_registry_with_bloks(['test_report_3'], None)
        registry.Attachment.Template.MyTemplate.file_ = file_
        page = registry.Attachment.WkHtml2Pdf.Page.insert(
            label="A4", size="A4")
        wkhtml2pdf = registry.Attachment.WkHtml2Pdf.insert(
            label="Custom", page=page)
        template = registry.Attachment.Template.MyTemplate.insert(
            template_path="report#=#common.py",
            filename='test',
            model="Model.System.Blok",
            wkhtml2pdf_configuration=wkhtml2pdf
        )
        document = registry.Attachment.Document.insert(template=template)
        get_file = document.get_file()
        self.assertTrue(get_file['file'])
        self.assertTrue(get_file['hash'])
        self.assertTrue(get_file['file_added_at'])

    def test_add_template_with_wkhtml2pdf_test_conf_changed(self):
        file_ = urandom(10)
        registry = self.init_registry_with_bloks(['test_report_3'], None)
        registry.Attachment.Template.MyTemplate.file_ = file_
        page = registry.Attachment.WkHtml2Pdf.Page.insert(
            label="A4", size="A4")
        page.refresh()
        wkhtml2pdf = registry.Attachment.WkHtml2Pdf.insert(
            label="Custom", page=page)
        wkhtml2pdf.refresh()
        template = registry.Attachment.Template.MyTemplate.insert(
            template_path="report#=#common.py",
            filename='test',
            model="Model.System.Blok",
            wkhtml2pdf_configuration=wkhtml2pdf
        )
        template.refresh()
        document = registry.Attachment.Document.insert(template=template)
        document.get_file()
        self.assertFalse(
            template.check_if_file_must_be_generated(document))
        wkhtml2pdf.margin_top = 20
        registry.flush()
        self.assertTrue(
            template.check_if_file_must_be_generated(document))

    def test_add_template_with_wkhtml2pdf_test_page_conf_changed(self):
        file_ = urandom(10)
        registry = self.init_registry_with_bloks(['test_report_3'], None)
        registry.Attachment.Template.MyTemplate.file_ = file_
        page = registry.Attachment.WkHtml2Pdf.Page.insert(
            label="A4", size="A4")
        page.refresh()
        wkhtml2pdf = registry.Attachment.WkHtml2Pdf.insert(
            label="Custom", page=page)
        wkhtml2pdf.refresh()
        template = registry.Attachment.Template.MyTemplate.insert(
            template_path="report#=#common.py",
            filename='test',
            model="Model.System.Blok",
            wkhtml2pdf_configuration=wkhtml2pdf
        )
        template.refresh()
        document = registry.Attachment.Document.insert(template=template)
        document.get_file()
        self.assertFalse(
            template.check_if_file_must_be_generated(document))
        page.size = "A3"
        registry.flush()
        self.assertTrue(
            template.check_if_file_must_be_generated(document))
