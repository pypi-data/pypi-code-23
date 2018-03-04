#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.command_mode import CommandMode


class EnableCommandMode(CommandMode):
    PROMPT = r'(\n|\r|^)\*?[^>]+?#\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''

    def __init__(self, resource_config, api):
        """Initialize Enable command mode - default command mode for Alcatel Shells"""

        self.resource_config = resource_config
        self._api = api
        CommandMode.__init__(self, self.PROMPT, self.ENTER_COMMAND, self.EXIT_COMMAND)


class ConfigCommandMode(CommandMode):
    PROMPT = r'(\n|\r|^)\*?[^>]+?>config#\s*$'
    ENTER_COMMAND = 'configure'
    EXIT_COMMAND = 'exit'

    def __init__(self, resource_config, api):
        """Initialize Config command mode"""

        self.resource_config = resource_config
        self._api = api
        CommandMode.__init__(self, self.PROMPT, self.ENTER_COMMAND, self.EXIT_COMMAND)


CommandMode.RELATIONS_DICT = {
    EnableCommandMode: {
        ConfigCommandMode: {},
    }
}
