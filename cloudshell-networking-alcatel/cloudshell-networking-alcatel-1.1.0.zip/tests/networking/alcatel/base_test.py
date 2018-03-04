import re
from unittest import TestCase

from cloudshell.devices.driver_helper import get_cli
from cloudshell.devices.standards.networking.configuration_attributes_structure import \
    create_networking_resource_from_context
from cloudshell.shell.core.driver_context import ResourceCommandContext, ResourceContextDetails
from mock import create_autospec, MagicMock

from cloudshell.networking.alcatel.cli.alcatel_cli_handler import AlcatelCliHandler

DEFAULT_PROMPT = 'A:ALU#'


class CliEmulator(object):
    def __init__(self, actions=None):
        self.command = None
        self.previous_resp = None

        self.actions = [
            ['^$', DEFAULT_PROMPT, None],
            ['^environment no more$', DEFAULT_PROMPT, None],
        ]

        if actions:
            self.actions.extend(actions)

    def _get_response(self):
        if self.command is None:
            return DEFAULT_PROMPT

        for action in self.actions:
            command, response, calls = action

            if re.search(command, self.command):
                if calls is None or calls > 0:
                    if calls is not None:
                        action[2] -= 1
                    if isinstance(response, list):
                        response = response.pop(0)

                    if isinstance(response, Exception):
                        raise response

                    return response
                else:
                    raise ValueError('"{}" command called more times than needed'.format(
                        self.command))

        raise KeyError('Doesn\'t find "{}" command'.format(self.command))

    def receive_all(self, timeout, logger):
        return self._get_response()

    def send_line(self, command, logger):
        self.command = command

    def check_calls(self):
        for command, response, calls in self.actions:
            if calls is not None and calls != 0:
                raise ValueError('{} not executed needed times ({} left)'.format(command, calls))


class BaseAlcatelTestCase(TestCase):
    SHELL_NAME = ''

    def create_context(self, attrs=None):
        context = create_autospec(ResourceCommandContext)
        context.resource = create_autospec(ResourceContextDetails)
        context.resource.name = 'Alcatel'
        context.resource.fullname = 'Alcatel'
        context.resource.family = 'CS_Router'
        context.resource.address = 'host'
        context.resource.attributes = {}

        attributes = {
            'User': 'user',
            'Password': 'password',
            'host': 'host',
            'CLI Connection Type': 'ssh',
            'Sessions Concurrency Limit': '1',
        }
        attributes.update(attrs or {})

        for key, val in attributes.items():
            context.resource.attributes['{}{}'.format(self.SHELL_NAME, key)] = val

        return context

    def _setUp(self, attrs=None):
        self.resource_config = create_networking_resource_from_context(
            self.SHELL_NAME, ['TiMOS'], self.create_context(attrs))
        self._cli = get_cli(int(self.resource_config.sessions_concurrency_limit))

        self.logger = MagicMock()
        self.api = MagicMock()
        self.api.DecryptPassword().Value.return_value = "password"

        self.cli_handler = AlcatelCliHandler(self._cli, self.resource_config, self.logger, self.api)

    def tearDown(self):
        self._cli._session_pool._session_manager._existing_sessions = []
