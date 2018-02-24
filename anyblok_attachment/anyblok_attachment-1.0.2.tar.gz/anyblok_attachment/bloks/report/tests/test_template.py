# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import BlokTestCase
from anyblok_attachment.bloks.report.exceptions import (
    RenderException, TemplateException, PathException)
from os import urandom


class TestTemplate(BlokTestCase):

    def test_without_render(self):
        template = self.registry.Attachment.Template.insert(
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        with self.assertRaises(RenderException):
            template.render({})

    def test_check_if_file_must_be_generated_1(self):
        template = self.registry.Attachment.Template.insert(
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        document = self.registry.Attachment.Document.insert(
            template=template)
        self.assertTrue(template.check_if_file_must_be_generated(document))

    def test_check_if_file_must_be_generated_2(self):
        template = self.registry.Attachment.Template.insert(
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        document = self.registry.Attachment.Document.insert()
        self.assertFalse(template.check_if_file_must_be_generated(document))

    def test_update_document(self):
        template = self.registry.Attachment.Template.insert(
            filename='test-{doc.uuid}-{doc.version}',
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        document = self.registry.Attachment.Document.insert(
            template=template)
        file_ = urandom(10)
        template.update_document(document, file_, {})
        self.assertEqual(document.file, file_)
        self.assertEqual(document.contenttype, 'plain/text')
        self.assertEqual(document.filesize, len(file_))
        filename = template.filename.format(doc=document)
        self.assertEqual(document.filename, filename)

    def test_get_parser(self):
        template = self.registry.Attachment.Template.insert(
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        self.assertIs(template.get_parser(), self.registry.Attachment.Parser)

    def test_get_template(self):
        template = self.registry.Attachment.Template.insert(
            template_path='report#=#tests/template.tmpl',
            model="Model.Attachment.Template")
        self.assertEqual(template.get_template(), "template\n")

    def test_without_parser(self):
        with self.assertRaises(TemplateException):
            self.registry.Attachment.Template.insert(
                template_path='report#=#tests/template.tmpl',
                parser_model='',
                model="Model.Attachment.Template")

    def test_without_template(self):
        with self.assertRaises((TemplateException, PathException)):
            self.registry.Attachment.Template.insert(
                template_path='',
                model="Model.Attachment.Template")
