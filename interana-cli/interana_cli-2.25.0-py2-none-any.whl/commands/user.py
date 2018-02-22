# Copyright 2017 Interana, Inc.
'''
ia user create
ia user enable
ia user disable
ia user list
ia user update
'''

from base import CommandHandler, SubCommandHandler, DoResult
from ..utils.shared_parsers import add_output_parameters
import json
import requests

class UserHandler(CommandHandler):

    name = 'user'
    description = 'Commands for managing users.'

    def __init__(self):
        CommandHandler.__init__(self)

        self.register_subcommands(CreateUser(),
                                  EnableUser(),
                                  DisableUser(),
                                  ListUsers(),
                                  UpdateUser())


class CreateUser(SubCommandHandler):

    name = 'create'
    description = 'Create a new user'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'username',
            help='Email address of the new user',
            type=str
        )
        parser.add_argument(
            'password',
            help='Password must be at least 8 characters in length',
            type=str
        )
        parser.add_argument(
            '--base-url',
            help="The base URL for the confirmation email. If not set, will default to the API node's public IP.",
            type=str
        )
        parser.add_argument(
            '--no-email',
            help='Create user without sending email or requiring confirmation',
            action='store_true'
        )
        parser.add_argument(
            '--role',
            help='Role(s) to give to created user (admin, user, publisher). Default is user',
            type=str,
            nargs='*',
            default='user'
        )
        return parser

    def post(self, url, authenticated=True, params=None, **kwargs):
        '''
        Overriding post method to add the hostname parameter. The hostname class variable isn't set until
        _prepare_kwargs is called.
        '''
        self._prepare_kwargs(authenticated, kwargs)
        return self._ok(
            requests.post(url.format(hostname=self.hostname),
                          params=params,
                          **kwargs))

    def do(self):
        if self.args.no_email:
            params = {
                'username': self.args.username,
                'password': self.args.password,
                'role_names': self.args.role
            }
            res = self.post('{hostname}/api/admin_create_user', data=params)
        else:
            params = {
                'c_username': self.args.username,
                'c_password': self.args.password,
                'c_password2': self.args.password,
                'base_url': self.args.base_url,
                'role_names': self.args.role
            }
            res = self.post('{hostname}/api/create_user', data=params)
        return self._handle_basic_response(res)


class EnableUser(SubCommandHandler):

    name = 'enable'
    description = 'Enable a user account'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'username',
            help='Username of account to enable',
            type=str
        )
        return parser

    def do(self):
        params = {
            'username': self.args.username,
            'action': 'enable',
        }
        res = self.post('{hostname}/api/toggle_user_status', data=params)
        return self._handle_basic_response(res)


class DisableUser(SubCommandHandler):

    name = 'disable'
    description = 'Disable a user account'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'username',
            help='Username of account to disable',
            type=str
        )
        return parser

    def do(self):
        params = {
            'username': self.args.username,
            'action': 'disable',
        }
        res = self.post('{hostname}/api/toggle_user_status', data=params)
        return self._handle_basic_response(res)


class ListUsers(SubCommandHandler):

    name = 'list'
    description = 'List registered users'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            '--include-disabled',
            help='Show disabled users',
            action='store_const',
            const=1,
            default=0,
        )
        return parser

    def do(self):
        params = {
            'include_disabled': self.args.include_disabled
        }
        res = self.get('{hostname}/api/list_users', params=params)
        users_res = json.loads(res.content)['data']
        return DoResult(entries=[[user['user_id'], user['username'], user['enabled'],
                                  ','.join(user['roles']), user['update_time']] for user in users_res],
                        headers=['User ID', 'Username', 'Enabled', 'Roles', 'Update Time'])


class UpdateUser(SubCommandHandler):
    name = 'update'
    description = 'Update an existing user'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'username',
            help='User to update',
            type=str
        )
        parser.add_argument(
            '--add-role',
            help='Add a role to the user (typically 3 choices: user, admin, publisher)',
            type=str
        )
        parser.add_argument(
            '--remove-role',
            help='Remove a role from the user (typically 3 choices: user, admin, publisher)',
            type=str
        )
        return parser

    def _update_role(self, action, role):
        if action == 'add':
            method = 'create'
            success_msg = 'Successfully added {} to {} role'
            failure_msg = 'Unable to add {} to {} role'
        else:
            method = 'delete'
            success_msg = 'Successfully removed {} from {} role'
            failure_msg = 'Unable to remove {} from {} role'
        method = 'create' if action == 'add' else 'delete'
        params = {
            'method': method,
            'role_name': role,
            'username': self.args.username
        }
        res = self.post('{hostname}/api/access/user_role', data=json.dumps(params))
        if (json.loads(res.content).get('result')):
            # happens when there are errors but there are messages
            return DoResult(message="Error: {}".format(json.loads(res.content)['result']))

        return self._handle_no_msg_response(res,
                                            success_msg.format(self.args.username, role),
                                            failure_msg.format(self.args.username, role))

    def do(self):
        result = None
        if self.args.add_role:
            result = self._update_role('add', self.args.add_role)
        elif self.args.remove_role:
            result = self._update_role('delete', self.args.remove_role)
        else:
            result = DoResult(message="Neither add-role nor remove-role was chosen. Please select one or the other.")

        return result
