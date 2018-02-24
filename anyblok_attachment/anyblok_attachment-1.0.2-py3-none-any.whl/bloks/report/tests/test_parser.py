# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import BlokTestCase


class TestParser(BlokTestCase):

    def test_serialize(self):
        Parser = self.registry.Attachment.Parser
        model = 'Model.registry.Attachment.Parser'
        data = {'a': 'Data'}
        self.assertEqual(Parser.serialize(model, data), data)

    def test_check_if_file_must_be_generated(self):
        Parser = self.registry.Attachment.Parser
        template = self.registry.Attachment.Template.insert(
            template_path='report#=#tests/test_parser.py',
            model="Model.Attachment.Template")
        document = self.registry.Attachment.Document.insert(
            template=template)
        self.assertFalse(
            Parser.check_if_file_must_be_generated(template, document))
