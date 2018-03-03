from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import tempfile
from builtins import *  # NOQA
from os import close
from unittest.case import TestCase

from click.testing import CliRunner
from yaml_test_case import YAMLTestCase
from zsl import inject
from zsl.application.containers.container import IoCContainer
from zsl.application.modules.alchemy_module import AlchemyModule
from zsl.application.modules.cli_module import CliModule
from zsl.application.modules.context_module import DefaultContextModule
from zsl.application.modules.logger_module import LoggerModule
from zsl.testing.db import IN_MEMORY_DB_SETTINGS
from zsl.testing.zsl import ZslTestCase
from zsl.testing.zsl import ZslTestConfiguration

from zsl_openapi.module import OpenAPICli
from zsl_openapi.module import OpenAPIModule


class TestContainer(IoCContainer):
    logger = LoggerModule
    database = AlchemyModule
    context = DefaultContextModule
    cli = CliModule
    open_api = OpenAPIModule


class OpenAPICliTestCase(ZslTestCase, YAMLTestCase, TestCase):
    ZSL_TEST_CONFIGURATION = ZslTestConfiguration('open_api_cli_test', container=TestContainer,
                                                  config_object=IN_MEMORY_DB_SETTINGS)

    def setUp(self):
        h, p = tempfile.mkstemp('.yml', 'zsl-openapi-test-')
        close(h)
        self._temp_filename = p

    @inject(open_api_cli=OpenAPICli)
    def testCli(self, open_api_cli):
        # type: (OpenAPICli)->None
        runner = CliRunner()

        result = runner.invoke(
            open_api_cli.open_api, [
                'generate',
                '--output', self._temp_filename,
                '--description', os.path.join(os.path.dirname(__file__), 'templates/test_cli_description_spec.yml'),
                '--package', 'tests.models',
                '--package', 'tests.models_cli'
            ]
        )

        self.assertEqual(0, result.exit_code, "No error expected, having error: {0}.".format(result.output))

        with open(self._temp_filename) as f:
            result_file_content = f.read()
        self.thenYAMLShouldBeEqual(
            'test_cli_description_result_spec.yml',
            result_file_content,
            "YAML must be correct",
        )

    def tearDown(self):
        os.unlink(self._temp_filename)
