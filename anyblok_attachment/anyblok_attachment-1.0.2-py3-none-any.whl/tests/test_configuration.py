# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_attachment.config import (
    define_attachment_wkhtml2pdf,
)
from anyblok.tests.testcase import TestCase
from anyblok.tests.test_config import MockArgumentParser


class TestArgsParseOption(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestArgsParseOption, cls).setUpClass()
        cls.parser = MockArgumentParser()
        cls.group = cls.parser.add_argument_group('label')
        cls.configuration = {}
        cls.function = {
            'define_attachment_wkhtml2pdf': define_attachment_wkhtml2pdf,
        }

    def test_define_attachment_wkhtml2pdf(self):
        self.function['define_attachment_wkhtml2pdf'](self.parser)
