from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from builtins import *  # NOQA
from io import BytesIO
from io import StringIO
from unittest.case import TestCase

from yaml_test_case import YAMLTestCase

from zsl_openapi import IS_PYTHON_3
from zsl_openapi.api import ApiDescription
from zsl_openapi.builders.description_info import fill
from zsl_openapi.generator import ApiGenerator


class FillTestCase(YAMLTestCase, TestCase):

    def testYamlFill(self):
        logging.getLogger('zsl_openapi').setLevel(logging.DEBUG)

        api_description = ApiDescription()
        yaml_spec = self.renderTemplate('test_cli_description_result_spec.yml')
        fill(yaml_spec, api_description)
        out = StringIO() if IS_PYTHON_3 else BytesIO()
        ApiGenerator().generate(api_description, out)

        self.thenYAMLShouldBeEqual(
            'test_cli_description_result_spec.yml',
            out.getvalue(),
            "YAML must be correct",
        )

    def testYamlFillFail(self):
        with self.assertRaises(TypeError):
            api_description = ApiDescription()
            fill(None, api_description)

        with self.assertRaises(TypeError):
            api_description = ApiDescription()
            fill([], api_description)
