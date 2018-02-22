# Copyright 2017 Interana, Inc.
'''
ia settings list
ia settings update
ia settings delete
'''

import json
from base import CommandHandler, SubCommandHandler, DoResult
from interana.utils.completers import SettingsApplicationCompleter, SettingsKeyCompleter
from interana.utils.shared_parsers import add_output_parameters


class SettingsHandler(CommandHandler):

    name = 'settings'
    description = 'Commands for managing settings.'

    def __init__(self):
        CommandHandler.__init__(self)

        self.register_subcommands(ListSettings(),
                                  UpdateSettings(),
                                  DeleteSettings())


class ListSettings(SubCommandHandler):

    name = 'list'
    description = 'List settings. All settings listed if application is not specified'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            '--application',
            help='Application of setting to be listed (e.g. "webapp")',
            type=str,
        ).completer = SettingsApplicationCompleter(self)
        return parser

    def do(self):
        params = {'application': self.args.application}

        if self.args.application == 'purifier':
            res = self.get('{hostname}/api/list_purifier_settings')
            content = json.loads(res.content)
            if content.get('success'):
                headers = ['Application', 'Table ID', 'Key', 'Value']
                entries = [['purifier', c['table_id'], c['key'], c['value']] for c in content['msg']]
            else:
                headers = ['Message', 'Success']
                entries = [[content['msg'], content['success']]]
        elif self.args.application:
            res = self.get('{hostname}/api/web_app', params=params)
            content = json.loads(res.content)
            if content.get('success'):
                headers = ['Application', 'Key', 'Value']
                entries = [[c['application'], c['key'], c['value']] for c in content['msg']]
            else:
                headers = ['Message', 'Success']
                entries = [[content['msg'], content['success']]]
        # no application specified, so we list both purifier and application settings
        else:
            res_app = self.get('{hostname}/api/web_app', params=params)
            res_purifier = self.get('{hostname}/api/list_purifier_settings')
            content_app = json.loads(res_app.content)
            content_purifier = json.loads(res_purifier.content)
            # both must be successful to list settings
            if content_app.get('success') and content_purifier.get('success'):
                headers = ['Application', 'Table ID', 'Key', 'Value']
                entries = [[c['application'], None, c['key'], c['value']] for c in content_app['msg']]
                entries += [['purifier', c['table_id'], c['key'], c['value']] for c in content_purifier['msg']]
            else:
                headers = ['Message', 'Success']
                entries = []
                if not content_app.get('success'):
                    entries += [[content_app['msg'], content_app['success']]]
                if not content_purifier.get('success'):
                    entries += [[content_purifier['msg'], content_purifier['success']]]
        return DoResult(entries=entries, headers=headers)


class UpdateSettings(SubCommandHandler):

    name = 'update'
    description = 'Update settings. Can specify table ID if updating purifier setting'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'application',
            help='Application of setting to be updated (e.g. "webapp")',
            type=str
        ).completer = SettingsApplicationCompleter(self)
        parser.add_argument(
            'key',
            help='Key of setting to be updated (e.g. "showABTestView")',
            type=str
        ).completer = SettingsKeyCompleter(self)
        parser.add_argument(
            'value',
            help='Value of setting to be updated',
            type=str
        )
        parser.add_argument(
            '-t',
            '--table-id',
            help='Table ID(s) of purifier setting to update. Can be single value '
            '(i.e. 1) or a comma separated list (i.e. 1,3,5). If not specified, '
            'setting is applied to all tables',
            type=str
        )
        parser.add_argument(
            '-f',
            '--force',
            help='Use to force a setting update without validation',
            action='store_const',
            const=1,
            default=0,
        )
        return parser

    def do(self):
        params_value = self.args.value
        try:
            params_value = json.loads(self.args.value)
        except ValueError:
            print 'NOTE: value could not be parsed as JSON, passing original string.'
            pass  # Not all settings are JSON - see HIG-9195.

        if self.args.application == 'purifier':
            params = {
                'table_id': self.args.table_id,
                'key': self.args.key,
                'value': params_value,
                'force': self.args.force
            }
            res = self.post('{hostname}/api/update_purifier_settings', data=params)
            return self._handle_basic_response(res)

        if self.args.table_id:
            error_msg = 'Table ID needs purifier specified as the application'
            return DoResult(entries=[[error_msg, 0]], headers=['Message', 'Success'])

        params = {
            'application': self.args.application,
            'key': self.args.key,
            'value': params_value,
            'force': self.args.force
        }
        res = self.post('{hostname}/api/web_app', data=json.dumps(params))
        return self._handle_basic_response(res)


class DeleteSettings(SubCommandHandler):

    name = 'delete'
    description = 'Delete settings. Can specify table ID if deleting purifier settings'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'application',
            help='Application of setting to be deleted (e.g. "webapp")',
            type=str
        ).completer = SettingsApplicationCompleter(self)
        parser.add_argument(
            'key',
            help='Key of setting to be deleted (e.g. "showABTestView")',
            type=str
        ).completer = SettingsKeyCompleter(self)
        parser.add_argument(
            '-t',
            '--table-id',
            help='Table ID(s) of purifier setting to delete. Can be single value '
            '(i.e. 1) or a comma separated list (i.e. 1,3,5). If not specified, '
            'setting deleted from all tables',
            type=str
        )
        return parser

    def do(self):
        if self.args.application == 'purifier':
            params = {
                'table_id': self.args.table_id,
                'key': self.args.key,
            }
            res = self.post('{hostname}/api/delete_purifier_settings', data=params)
            return self._handle_basic_response(res)

        # for all other non-purifier applications
        if self.args.table_id:
            error_msg = 'Table ID needs purifier specified as the application'
            return DoResult(entries=[[error_msg, 0]], headers=['Message', 'Success'])

        params = {
            'application': self.args.application,
            'key': self.args.key,
        }
        res = self.post('{hostname}/api/delete_app_settings', data=params)
        return self._handle_basic_response(res)
