# -*- coding: utf-8 -*-
"""Extension with interface to bugtracking and test management systems

.. module:: trackapps.trackapps
   :platform: Unix
   :synopsis: Extension with interface to bugtracking and test management systems
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from hydratk.core import extension, bootstrapper
from hydratk.lib.console.commandlinetool import CommandlineTool
from os import path
from importlib import import_module
import hydratk.lib.system.config as syscfg

dep_modules = {
    'hydratk': {
        'min-version': '0.5.0',
        'package': 'hydratk'
    },
    'hydratk.lib.network': {
        'min-version': '0.2.0',
        'package': 'hydratk-lib-network'
    }
}

apps = {
    'qc': 'qc',
    'bugzilla': 'bugzilla',
    'mantis': 'mantis',
    'trac': 'trac',
    'jira': 'jira',
    'testlink': 'testlink'
}


class Extension(extension.Extension):
    """Class Extension
    """

    def _init_extension(self):
        """Method initializes extension

        Args:
           none

        Returns:
           void

        """

        self._ext_id = 'trackapps'
        self._ext_name = 'TrackApps'
        self._ext_version = '0.1.1'
        self._ext_author = 'Petr Rašek <bowman@hydratk.org>, HydraTK team <team@hydratk.org>'
        self._ext_year = '2016-2018'

        if (not self._check_dependencies()):
            exit(0)

    def _check_dependencies(self):
        """Method checks dependent modules

        Args:            
           none

        Returns:
           bool    

        """

        return bootstrapper._check_dependencies(dep_modules, 'hydratk-ext-trackapps')

    def _uninstall(self):
        """Method returns additional uninstall data 

        Args:            
           none

        Returns:
           tuple: list (files), list (modules)   

        """

        files = [
            '/usr/share/man/man1/trackapps.1',
            '{0}/hydratk/conf.d/hydratk-ext-trackapps.conf'.format(syscfg.HTK_ETC_DIR)
        ]

        return files, dep_modules

    def _register_actions(self):
        """Method registers command hooks

        Args:
           none

        Returns:
           void

        """

        if (self._mh.cli_cmdopt_profile == 'trackapps'):
            self._register_standalone_actions()
        else:
            self._register_htk_actions()

    def _register_htk_actions(self):
        """Method registers command hooks

        Args:  
           none        

        Returns:
           void

        """

        self._mh.match_cli_command('track')

        hook = [
            {'command': 'track', 'callback': self.handle_track}
        ]
        self._mh.register_command_hook(hook)

        self._mh.match_long_option('tr-app', True, 'tr-app')
        self._mh.match_long_option('tr-action', True, 'tr-action')
        self._mh.match_long_option('tr-type', True, 'tr-type')
        self._mh.match_long_option('tr-input', True, 'tr-input')
        self._mh.match_long_option('tr-output', True, 'tr-output')
        self._mh.match_long_option('tr-url', True, 'tr-url')
        self._mh.match_long_option('tr-user', True, 'tr-user')
        self._mh.match_long_option('tr-passw', True, 'tr-passw')
        self._mh.match_long_option('tr-dev-key', True, 'tr-dev-key')
        self._mh.match_long_option('tr-domain', True, 'tr-domain')
        self._mh.match_long_option('tr-project', True, 'tr-project')
        self._mh.match_long_option('tr-id', True, 'tr-id')
        self._mh.match_long_option('tr-fields', True, 'tr-fields')
        self._mh.match_long_option('tr-query', True, 'tr-query')
        self._mh.match_long_option('tr-order-by', True, 'tr-order-by')
        self._mh.match_long_option('tr-limit', True, 'tr-limit')
        self._mh.match_long_option('tr-offset', True, 'tr-offset')
        self._mh.match_long_option('tr-page', True, 'tr-page')
        self._mh.match_long_option('tr-per-page', True, 'tr-per-page')
        self._mh.match_long_option('tr-params', True, 'tr-params')
        self._mh.match_long_option('tr-path', True, 'tr-path')
        self._mh.match_long_option('tr-steps', True, 'tr-steps')

    def _register_standalone_actions(self):
        """Method registers command hooks for standalone mode

        Args:  
           none        

        Returns:
           void

        """

        option_profile = 'trackapps'
        help_title = '{h}' + self._ext_name + ' v' + self._ext_version + '{e}'
        cp_string = '{u}' + "(c) " + self._ext_year + \
            " " + self._ext_author + '{e}'
        self._mh.set_cli_appl_title(help_title, cp_string)

        self._mh.match_cli_command('run', option_profile)

        hook = [
            {'command': 'run', 'callback': self.handle_track}
        ]
        self._mh.register_command_hook(hook)

        self._mh.match_cli_command('help', option_profile)

        self._mh.match_long_option(
            'app', True, 'tr-app', False, option_profile)
        self._mh.match_long_option(
            'action', True, 'tr-action', False, option_profile)
        self._mh.match_long_option(
            'type', True, 'tr-type', False, option_profile)
        self._mh.match_long_option(
            'input', True, 'tr-input', False, option_profile)
        self._mh.match_long_option(
            'output', True, 'tr-output', False, option_profile)
        self._mh.match_long_option(
            'url', True, 'tr-url', False, option_profile)
        self._mh.match_long_option(
            'user', True, 'tr-user', False, option_profile)
        self._mh.match_long_option(
            'passw', True, 'tr-passw', False, option_profile)
        self._mh.match_long_option(
            'dev-key', True, 'tr-dev-key', False, option_profile)
        self._mh.match_long_option(
            'domain', True, 'tr-domain', False, option_profile)
        self._mh.match_long_option(
            'project', True, 'tr-project', False, option_profile)
        self._mh.match_long_option('id', True, 'tr-id', False, option_profile)
        self._mh.match_long_option(
            'fields', True, 'tr-fields', False, option_profile)
        self._mh.match_long_option(
            'query', True, 'tr-query', False, option_profile)
        self._mh.match_long_option(
            'order-by', True, 'tr-order-by', False, option_profile)
        self._mh.match_long_option(
            'limit', True, 'tr-limit', False, option_profile)
        self._mh.match_long_option(
            'offset', True, 'tr-offset', False, option_profile)
        self._mh.match_long_option(
            'page', True, 'tr-page', False, option_profile)
        self._mh.match_long_option(
            'per-page', True, 'tr-per-page', False, option_profile)
        self._mh.match_long_option(
            'params', True, 'tr-params', False, option_profile)
        self._mh.match_long_option(
            'path', True, 'tr-path', False, option_profile)
        self._mh.match_long_option(
            'steps', True, 'tr-steps', False, option_profile)

        self._mh.match_cli_option(
            ('c', 'config'), True, 'config', False, option_profile)
        self._mh.match_cli_option(
            ('d', 'debug'), True, 'debug', False, option_profile)
        self._mh.match_cli_option(
            ('e', 'debug-channel'), True, 'debug-channel', False, option_profile)
        self._mh.match_cli_option(
            ('l', 'language'), True, 'language', False, option_profile)
        self._mh.match_cli_option(
            ('m', 'run-mode'), True, 'run-mode', False, option_profile)
        self._mh.match_cli_option(
            ('f', 'force'), False, 'force', False, option_profile)
        self._mh.match_cli_option(
            ('i', 'interactive'), False, 'interactive', False, option_profile)
        self._mh.match_cli_option(
            ('h', 'home'), False, 'home', False, option_profile)

    def init_client(self, app, *args, **kwargs):
        """Client factory method

        Args:            
            app (str): application, qc|bugzilla|mantis|trac|jira|testlink
            args (args): arguments 
            kwargs (kwargs): key value arguments

        Returns:
            obj: Client

        Raises:
            error: NotImplementedError

        """

        self._app = app.lower()
        if (self._app in apps):
            mod = import_module(
                'hydratk.extensions.trackapps.{0}'.format(apps[app]))
            return mod.Client(*args, **kwargs)
        else:
            raise NotImplementedError('Unknown application:{0}'.format(app))

    def handle_track(self):
        """Method handles command track

        Args:
           none

        Returns:
           void   

        """

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_received_cmd', 'track'), self._mh.fromhere())

        app = CommandlineTool.get_input_option('tr-app')
        action = CommandlineTool.get_input_option('tr-action')

        if (not app):
            print('Missing option app')
        elif (app.lower() not in apps):
            print('Application not in qc|bugzilla|mantis|trac|jira|testlink')
        elif (not action):
            print('Missing option action')
        elif (action not in ['read', 'create', 'update', 'delete']):
            print('Action not in read|create|update|delete')
        elif (action == 'delete' and app.lower() not in ['qc', 'mantis', 'trac']):
            print('Application {0} doesn\'t support {1}'.format(app, action))
        else:

            self._client = self.init_client(app)
            self._cfg = self._mh.cfg['Extensions']['TrackApps'][self._app]

            url = CommandlineTool.get_input_option('tr-url')
            if (not url):
                if ('url' in self._cfg and self._cfg['url'] != None):
                    url = self._cfg['url']
                else:
                    print('Enter url')
                    url = raw_input(':')

            user = CommandlineTool.get_input_option('tr-user')
            if (not user and self._app != 'testlink'):
                if ('user' in self._cfg and self._cfg['user'] != None):
                    user = self._cfg['user']
                else:
                    print('Enter username')
                    user = raw_input(':')

            passw = CommandlineTool.get_input_option('tr-passw')
            if (not passw and self._app != 'testlink'):
                if ('passw' in self._cfg and self._cfg['passw'] != None):
                    passw = self._cfg['passw']
                else:
                    print('Enter password')
                    passw = raw_input(':')

            dev_key = CommandlineTool.get_input_option('tr-dev-key')
            if (not dev_key and self._app == 'testlink'):
                if ('dev_key' in self._cfg and self._cfg['dev_key'] != None):
                    dev_key = self._cfg['dev_key']
                else:
                    print('Enter dev_key')
                    dev_key = raw_input(':')

            domain = CommandlineTool.get_input_option('tr-domain')
            if (not domain and self._app == 'qc'):
                if ('domain' in self._cfg and self._cfg['domain'] != None):
                    domain = self._cfg['domain']
                else:
                    print('Enter domain')
                    domain = raw_input(':')

            project = CommandlineTool.get_input_option('tr-project')
            if (not project and self._app in ['qc', 'mantis', 'trac', 'jira', 'testlink']):
                if ('project' in self._cfg and self._cfg['project'] != None):
                    project = self._cfg['project']
                else:
                    print('Enter project')
                    project = raw_input(':')

            self._entity = CommandlineTool.get_input_option('tr-type')
            if (not self._entity):
                self._entity = 'defect'
            if (self._app == 'qc' and self._entity not in ['defect', 'test-folder', 'test', 'test-set-folder', 'test-set', 'test-instance']):
                print(
                    'Type not in defect|test-folder|test|test-set-folder|test-set|test-instance')
                return
            elif (self._app == 'testlink'):
                if (self._entity not in ['test', 'test-suite', 'test-plan', 'build']):
                    print('Type not in test|test-suite|test-plan|build')
                    return
                elif (action == 'read' and self._entity not in ['test', 'test-suite', 'test-plan']):
                    print(
                        'Type not in test|test-suite|test-plan for action read')
                    return
                elif (action == 'update' and self._entity not in ['test', 'test-plan']):
                    print('Type not in test|test-plan for action update')
                    return

            if (self._app == 'qc'):
                res = self._client.connect(url, user, passw, domain, project)
            elif (self._app == 'bugzilla'):
                res = self._client.connect(url, user, passw)
            elif (self._app in ['mantis', 'trac', 'jira']):
                res = self._client.connect(url, user, passw, project)
            elif (self._app == 'testlink'):
                res = self._client.connect(url, dev_key, project)

            if (not res):
                print('Connection error')
                return

            if (action == 'read'):
                self.read()
            elif (action == 'create'):
                self.create()
            elif (action == 'update'):
                self.update()
            elif (action == 'delete'):
                self.delete()

            if (self._app in ['qc', 'bugzilla']):
                self._client.disconnect()

    def read(self):
        """Method handles read action

        Args:
           none

        Returns:
           void

        """

        id = CommandlineTool.get_input_option('tr-id')
        if (not id):
            id = None

        fields = CommandlineTool.get_input_option('tr-fields')
        if (not fields):
            fields = None

        query = CommandlineTool.get_input_option('tr-query')
        if (not query):
            query = None

        order_by_in = CommandlineTool.get_input_option('tr-order-by')
        if (order_by_in != False):
            order_by = {}
            order_by_in = order_by_in.split(',')
            for param in order_by_in:
                rec = param.split(':')
                key = rec[0]
                order_by[key] = rec[1]
        else:
            order_by = None

        limit = CommandlineTool.get_input_option('tr-limit')
        if (not limit):
            limit = None

        offset = CommandlineTool.get_input_option('tr-offset')
        if (not offset):
            offset = None

        page = CommandlineTool.get_input_option('tr-page')
        if (not page):
            page = -1

        per_page = CommandlineTool.get_input_option('tr-per-page')
        if (not per_page):
            per_page = -1

        if (self._app == 'qc'):
            if (self._entity in ['test-folder', 'test-set-folder']):
                path = CommandlineTool.get_input_option('tr-path')
                if (not path):
                    print('Enter path')
                    path = raw_input(':')
                res, records = self._client.read_test_folder(
                    path, self._entity)
            elif (self._entity == 'test-set'):
                if (not id):
                    print('Enter test set id')
                    id = raw_input(':')
                res, records = self._client.read_test_set(int(id))
            else:
                res, records = self._client.read(
                    id, self._entity, fields, query, order_by, limit, offset)

        elif (self._app == 'testlink'):
            if (self._entity == 'test-suite'):
                path = CommandlineTool.get_input_option('tr-path')
                if (not path):
                    print('Enter path')
                    path = raw_input(':')
                res, records = self._client.read_test_suite(
                    path, fields=fields)
            elif (self._entity == 'test-plan'):
                if (not id):
                    print('Enter plan id')
                    id = raw_input(':')
                res, records = self._client.read_test_plan(
                    plan_id=id, fields=fields)
            elif (self._entity == 'test'):
                if (not id):
                    print('Enter test id')
                    id = raw_input(':')
                res, records = self._client.read_test(id, fields)

        elif (self._app == 'bugzilla'):
            res, records = self._client.read(id, fields, query, limit, offset)
        elif (self._app == 'mantis'):
            res, records = self._client.read(id, fields, page, per_page)
        elif (self._app == 'trac'):
            res, records = self._client.read(id, fields, query)
        elif (self._app == 'jira'):
            res, records = self._client.read(id, fields, query, limit, offset)

        if (res):
            output = CommandlineTool.get_input_option('tr-output')
            if (not output):
                print(records)
            else:
                with (open(output, 'w')) as f:
                    f.write(str(records))
        else:
            print('Read error')

    def create(self):
        """Method create action

        Args:
           none

        Returns:
           void

        """

        if (self._app in ['qc', 'testlink']):
            params = {}
            if (self._entity in self._client._default_values):
                params = self._client._default_values[self._entity]
        else:
            params = self._client.default_values

        params_in = CommandlineTool.get_input_option('tr-params')
        if (params_in != False):
            params_in = params_in.split(',')
            for param in params_in:
                rec = param.split(':')
                key = rec[0]
                params[key] = rec[1]

        input = CommandlineTool.get_input_option('tr-input')
        if (input != False and path.exists(input)):
            with open(input, 'r') as f:
                params['description'] = f.read()

        if ('required_fields' in self._cfg and self._cfg['required_fields'] != None):
            if (self._app == 'qc'):
                if (self._entity in self._cfg['required_fields'] and
                        self._cfg['required_fields'][self._entity] != None):
                    fields = self._cfg['required_fields'][
                        self._entity].split(',')
                else:
                    fields = []
            else:
                fields = self._cfg['required_fields'].split(',')

            lov = {}
            if ('lov' in self._cfg and self._cfg['lov'] != None):
                if (self._app == 'qc'):
                    if (self._entity in self._cfg['lov'] and
                            self._cfg['lov'][self._entity] != None):
                        lov = {}
                        expr = self._cfg['lov'][self._entity]
                        if (expr != None):
                            lov_params = expr.split('#')
                            for param in lov_params:
                                conf = param.split('%')
                                lov[conf[0]] = conf[1]
                else:
                    lov = self._cfg['lov']

                if (len(lov) > 0):
                    for key, value in lov.items():
                        lov[key] = value.split(',')

            for field in fields:

                if (field not in params):
                    print('Enter required field: {0}'.format(field))

                    if (field not in lov):
                        value = raw_input(':')
                        params[field] = value

                    else:
                        prompt = ''
                        values = lov[field]
                        cnt = len(values)
                        for i in range(0, cnt):
                            prompt += '{0} - {1}\n'.format(i + 1, values[i])

                        valid = False
                        while (not valid):
                            try:
                                idx = int(raw_input('{0}'.format(prompt))) - 1
                            except ValueError:
                                idx = -1

                            if (idx >= 0 and idx < cnt):
                                valid = True
                            else:
                                print(
                                    'Wrong choice, enter required field: {0}'.format(field))

                        params[field] = values[idx]

        steps_in = CommandlineTool.get_input_option('tr-steps')
        steps = []
        if (steps_in != False):
            steps_in = steps_in.split('|')
            for step_in in steps_in:
                step = {}
                for param in step_in.split(','):
                    rec = param.split(':')
                    key = rec[0]
                    step[key] = rec[1]
                steps.append(step)

        if (self._app == 'qc'):
            if (self._entity in ('defect', 'test-instance')):
                id = self._client.create(self._entity, params)
            else:
                path = CommandlineTool.get_input_option('tr-path')
                if (not path):
                    print('Enter path')
                    path = raw_input(':')
                if (self._entity == 'test'):
                    id = self._client.create_test(path, params)
                elif (self._entity == 'test-set'):
                    id = self._client.create_test_set(path, params)
                else:
                    folders = path.split('/')
                    id = self._client.create_test_folder(
                        '/'.join(folders[:-1]), folders[-1], self._entity)

        elif (self._app == 'testlink'):
            if (self._entity == 'test-suite'):
                path = CommandlineTool.get_input_option('tr-path')
                if (not path):
                    print('Enter path')
                    path = raw_input(':')
                details = params['details'] if ('details' in params) else None

                folders = path.split('/')
                id = self._client.create_test_suite(
                    '/'.join(folders[:-1]), folders[-1], details)

            elif (self._entity == 'test-plan'):
                name = params['name'] if ('name' in params) else None
                if ('name' not in params):
                    print('Enter name')
                    name = raw_input(':')
                notes = params['notes'] if ('notes' in params) else None

                id = self._client.create_test_plan(name, notes)

            elif (self._entity == 'build'):
                plan = params['plan'] if ('plan' in params) else None
                if ('plan' not in params):
                    print('Enter plan id')
                    plan = raw_input(':')
                name = params['name'] if ('name' in params) else None
                if ('name' not in params):
                    print('Enter name')
                    name = raw_input(':')
                notes = params['notes'] if ('notes' in params) else None

                id = self._client.create_build(plan, name, notes)

            elif (self._entity == 'test'):
                path = CommandlineTool.get_input_option('tr-path')
                if (not path):
                    print('Enter path')
                    path = raw_input(':')

                id = self._client.create_test(path, params, steps)

        else:
            id = self._client.create(params)

        if (id != None):
            print('Record {0} created'.format(id))
        else:
            print('Create error')

    def update(self):
        """Method handles update action

        Args:
           none

        Returns:
           void

        """

        id = CommandlineTool.get_input_option('tr-id')
        if (not id):
            print('Enter id')
            id = raw_input(':')

        params_in = CommandlineTool.get_input_option('tr-params')
        if (not params_in):
            params = {}
        else:
            params_in = params_in.split(',')
            params = {}
            for param in params_in:
                rec = param.split(':')
                params[rec[0]] = rec[1]

        input = CommandlineTool.get_input_option('tr-input')
        if (input != False and path.exists(input)):
            with open(input, 'r') as f:
                params['description'] = f.read()

        if (self._app == 'qc'):
            res = self._client.update(id, self._entity, params)
        elif (self._app == 'testlink'):
            if (self._entity == 'test-plan'):
                test_id = params['test'] if ('test' in params) else None
                if ('test' not in params):
                    print('Enter test id')
                    test_id = raw_input(':')

                res = self._client.add_test_to_plan(test=test_id, plan_id=id)

            elif (self._entity == 'test'):
                plan_id = params['plan'] if ('plan' in params) else None
                if ('plan' not in params):
                    print('Enter plan id')
                    plan_id = raw_input(':')
                status = params['status'] if ('status' in params) else 'p'
                notes = params['notes'] if ('notes' in params) else None
                build_id = params['build'] if ('build' in params) else None

                res = self._client.update_test_execution(
                    id, status, notes, plan_id=plan_id, build_id=build_id)

        else:
            res = self._client.update(id, params)

        if (res):
            print('Record {0} updated'.format(id))
        else:
            print('Update error')

    def delete(self):
        """Method handles delete action

        Args:
           none

        Returns:
           void

        """

        id = CommandlineTool.get_input_option('tr-id')
        if (not id):
            print('Enter id')
            id = raw_input(':')

        if (self._app == 'qc'):
            res = self._client.delete(id, self._entity)
        else:
            res = self._client.delete(id)
        if (res):
            print('Record {0} deleted'.format(id))
        else:
            print('Delete error')
