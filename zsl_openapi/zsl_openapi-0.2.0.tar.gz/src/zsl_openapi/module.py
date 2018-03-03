"""
:mod:`zsl_openapi.module`
-------------------------

OpenAPI module allows you to generate YAML files with the OpenAPI specification
of the ZSL API.

It adds a CLI so that the module can be used via standard ZSL cli.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import importlib
import logging
import sys
import traceback
from builtins import *  # NOQA

import click
from injector import Binder  # NOQA
from injector import Module
from injector import provides
from injector import singleton
from zsl import Config
from zsl import inject
from zsl.application.modules.cli_module import ZslCli
from zsl.utils.injection_helper import simple_bind

from zsl_openapi.api import ApiDescription
from zsl_openapi.builders.description_info import FileApiDescriptionInfoBuilder
from zsl_openapi.builders.models import PersistentModelsApiDescriptionBuilder
from zsl_openapi.builders.tasks import TasksApiDescriptionBuilder
from zsl_openapi.configuration import OpenAPIConfiguration
from zsl_openapi.generator import ApiGenerator


class OpenAPIModule(Module):
    """Adds Alembic support for migrations."""

    OPEN_API_CONFIG_NAME = 'OPEN_API'

    @provides(OpenAPIConfiguration)
    @inject(config=Config)
    def provide_alembic_configuration(self, config):
        # type: (Config) -> OpenAPIConfiguration
        return config.get(OpenAPIModule.OPEN_API_CONFIG_NAME)

    def configure(self, binder):
        # type: (Binder) -> None
        simple_bind(binder, OpenAPICli, singleton)


class OpenAPICli(object):
    """Alembic Cli interface support."""

    @inject(zsl_cli=ZslCli)
    def __init__(self, zsl_cli):
        # type: (ZslCli) -> None
        logging.getLogger(__name__).debug("Creating OpenAPI CLI.")

        @zsl_cli.cli.group(help='Run OpenAPI tasks.')
        def open_api():
            pass

        @open_api.command()
        @click.option('--output', help="Output file with yml extension.")
        @click.option('--description', help="Description YAML file containing basic information.")
        @click.option('--package', help="Package(s) containing the models.", multiple=True)
        def generate(output, description, package):
            api_description = ApiDescription()
            try:
                FileApiDescriptionInfoBuilder(description).build(api_description)
                for single_package in package:
                    mod = importlib.import_module(single_package)
                    PersistentModelsApiDescriptionBuilder(mod).build(api_description)
                TasksApiDescriptionBuilder().build(api_description)
            except Exception as e:
                traceback.print_exc()
                print(e)
                sys.exit(1)
            with open(output, 'w') as f:
                ApiGenerator().generate(api_description, f)

        self._open_api = open_api

    @property
    def open_api(self):
        return self._open_api

    def __call__(self, *args, **kwargs):
        self._open_api()
