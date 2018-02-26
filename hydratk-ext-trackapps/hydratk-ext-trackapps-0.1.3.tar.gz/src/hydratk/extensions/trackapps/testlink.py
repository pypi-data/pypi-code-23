# -*- coding: utf-8 -*-
"""Client for TestLink

.. module:: trackapps.testlink
   :platform: Unix
   :synopsis: Client for TestLink
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

"""
Events:
-------
track_before_connect
track_after_connect
track_before_read
track_after_read
track_before_create
track_after_create
track_before_update
track_after_update
track_before_read_suite
track_after_rest_suite
track_before_read_plan
track_after_read_plan

"""

from hydratk.core.masterhead import MasterHead
from hydratk.core import event
from hydratk.lib.network.rpc.client import RPCClient


class Client(object):
    """Class Client
    """

    _mh = None
    _client = None
    _url = None
    _dev_key = None
    _project = None
    _project_id = None
    _return_fields = None
    _default_values = {}
    _is_connected = None

    def __init__(self):
        """Class constructor

        Called when the object is initialized 

        Args:  
           none

        """

        self._mh = MasterHead.get_head()
        self._client = RPCClient('XMLRPC')

        cfg = self._mh.cfg['Extensions']['TrackApps']['testlink']
        if ('return_fields' in cfg and cfg['return_fields'] != None):
            self._return_fields = cfg['return_fields'].split(',')
        if ('default_values' in cfg and cfg['default_values'] != None):
            self._default_values = cfg['default_values']
        if ('url' in cfg and cfg['url'] != None):
            self._url = cfg['url']
        if ('dev_key' in cfg and cfg['dev_key'] != None):
            self._dev_key = cfg['dev_key']
        if ('project' in cfg and cfg['project'] != None):
            self._project = cfg['project']

    @property
    def client(self):
        """ client property getter """

        return self._client

    @property
    def url(self):
        """ url property getter """

        return self._url

    @property
    def dev_key(self):
        """ dev key property getter """

        return self._dev_key

    @property
    def project(self):
        """ project property getter """

        return self._project

    @property
    def project_id(self):
        """ project id property getter """

        return self._project_id

    @property
    def return_fields(self):
        """ return_fields property getter """

        return self._return_fields

    @property
    def default_values(self):
        """ default_values property getter """

        return self._default_values

    @property
    def is_connected(self):
        """ is_connected property getter """

        return self._is_connected

    def connect(self, url=None, dev_key=None, project=None):
        """Method connects to TestLink

        Args:    
           url (str): URL        
           dev_key (str): development key to access API
           project (str): project

        Returns:
           bool: result

        Raises:
           event: track_before_connect
           event: track_after_connect

        """

        message = 'url:{0}, dev_key:{1}, project:{2}'.format(
            url, dev_key, project)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_connecting', message), self._mh.fromhere())

        if (url == None):
            url = self._url
        if (dev_key == None):
            dev_key = self._dev_key
        if (project == None):
            project = self._project

        ev = event.Event('track_before_connect', url, dev_key, project)
        if (self._mh.fire_event(ev) > 0):
            url = ev.argv(0)
            dev_key = ev.argv(1)
            project = ev.argv(2)

        if (ev.will_run_default()):
            self._url = url
            self._dev_key = dev_key
            self._project = project

            url = self._url + '/testlink/lib/api/xmlrpc/v1/xmlrpc.php'
            params = {
                'testprojectname': self._project, 'devKey': self._dev_key}
            res = self._client.init_proxy(url)

        result = False
        if (res != None):
            body = self._client.call_method('tl.getTestProjectByName', params)

            if (body != None):
                if (body.__class__.__name__ == 'list'):
                    body = body[0]

                self._project_id = int(body['id']) if (
                    'id' in body.keys()) else None
                if (self._project_id != None):
                    self._is_connected = True
                    self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                        'track_connected'), self._mh.fromhere())
                    ev = event.Event('track_after_connect')
                    self._mh.fire_event(ev)
                    result = True
                else:
                    self._mh.demsg('htk_on_error', self._mh._trn.msg(
                        'track_error', body['code'], body['message']), self._mh.fromhere())

        return result

    def read_test_suite(self, path, steps=True, fields=None):
        """Method reads tests under test suite

        Args: 
           path (str): suite path
           steps (bool): get steps
           fields (list): test fields to be returned, default all

        Returns:
           tuple: result (bool), records (dict), key - test suite, value - list of tests

        Raises:
           event: track_before_read_suite
           event: track_after_read_suite                           

        """

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('track_reading_folder', path, 'test_suite'),
                      self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False, None

        if (fields == None and self._return_fields != None):
            fields = self._return_fields

        ev = event.Event('track_before_read_suite', path, steps, fields)
        if (self._mh.fire_event(ev) > 0):
            path = ev.argv(0)
            steps = ev.argv(1)
            fields = ev.argv(2)

        if (ev.will_run_default()):

            id = self._get_suite(path)
            if (id == None):
                return False, None

            details = 'full' if (steps) else 'simple'
            params = {
                'devKey': self._dev_key, 'testsuiteid': id, 'details': details}
            recs = self._client.call_method(
                'tl.getTestCasesForTestSuite', params)
            if (recs == None):
                return False, None

            tests = {}
            suites = {str(id): {'name': path, 'parent': None, 'path': True}}
            for record in recs:
                parent = str(record['parent_id'])
                parent_orig = parent

                while (parent != None and parent not in suites):
                    params = {'devKey': self._dev_key, 'testsuiteid': parent}
                    rec = self._client.call_method(
                        'tl.getTestSuiteByID', params)
                    suites[parent] = {
                        'name': rec['name'], 'parent': str(rec['parent_id']), 'path': False}
                    parent = str(rec['parent_id'])

                for key, value in suites.items():
                    parent = None
                    while (not suites[key]['path']):
                        parent = suites[value['parent']] if (
                            parent == None) else parent['parent']
                        suites[key][
                            'name'] = '{0}/{1}'.format(parent['name'], suites[key]['name'])
                        if (parent['parent'] == None):
                            suites[key]['path'] = True

                suite_name = suites[parent_orig]['name']
                if (suite_name not in tests):
                    tests[suite_name] = []

                record_new = {}
                for key, value in record.items():
                    if (fields == None or key in fields):
                        record_new[key] = value

                if (record_new != {}):
                    tests[suite_name].append(record_new)

        if (recs != None):
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('track_folder_read', len(recs)),
                          self._mh.fromhere())
            ev = event.Event('track_after_read_suite')
            self._mh.fire_event(ev)
            return True, tests

    def create_test_suite(self, path, name, details=None):
        """Method creates test folder on path

        Args: 
           path (str): suite path
           name (str): suite name
           details (str): suite details

        Returns:
           int: suite id

        Raises:
           event: track_before_create
           event: track_after_create

        """

        params = 'path:{0}, name:{1}, details:{2}'.format(path, name, details)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_creating', 'test_suite', params), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return None

        ev = event.Event('track_before_create', path, name, details)
        if (self._mh.fire_event(ev) > 0):
            path = ev.argv(0)
            name = ev.argv(1)
            details = ev.argv(2)

        if (ev.will_run_default()):
            suite = self._get_suite(path)
            if (suite == None):
                return None

            params = {'devKey': self._dev_key, 'testprojectid': self._project_id,
                      'testsuitename': name, 'parentid': suite, 'details': details}
            body = self._client.call_method('tl.createTestSuite', params)

        id = None
        if (body != None):
            if (body.__class__.__name__ == 'list'):
                body = body[0]

            id = int(body['id']) if (
                'id' in body.keys() and int(body['id']) > 0) else None
            if (id != None):
                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_created', id), self._mh.fromhere())
                ev = event.Event('track_after_create')
                self._mh.fire_event(ev)
            else:
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_error', -1, body['msg']), self._mh.fromhere())

        return id

    def read_test_plan(self, plan=None, plan_id=None, build_id=None, fields=None):
        """Method reads tests under plan

        Args:
           plan (str): plan name, will be translated to plan_id
           plan_id (int): plan_id
           build_id (int): build id, latest build will be used if not specified
           fields (list): test fields to be returned, default all   

        Returns:
           tuple: result (bool), records (list of dict)

        Raises:
           event: track_before_read_plan
           event: track_after_read_plan                           

        """

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('track_reading_folder', plan, 'test_plan'),
                      self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False, None

        if (fields == None and self._return_fields != None):
            fields = self._return_fields

        ev = event.Event(
            'track_before_read_plan', plan, plan_id, build_id, fields)
        if (self._mh.fire_event(ev) > 0):
            plan = ev.argv(0)
            plan_id = ev.argv(1)
            build_id = ev.argv(2)
            fields = ev.argv(3)

        if (ev.will_run_default()):

            if (plan != None):
                params = {
                    'devKey': self._dev_key, 'testprojectname': self._project, 'testplanname': plan}
                body = self._client.call_method('tl.getTestPlanByName', params)
                if (body.__class__.__name__ == 'list'):
                    body = body[0]

                plan_id = body['id'] if ('id' in body.keys()) else None
                if (plan_id == None):
                    self._mh.demsg('htk_on_error', self._mh._trn.msg(
                        'track_error', body['code'], body['message']), self._mh.fromhere())
                    return False, None

            if (build_id == None):
                params = {'devKey': self._dev_key, 'testplanid': plan_id}
                body = self._client.call_method(
                    'tl.getLatestBuildForTestPlan', params)
                if (body.__class__.__name__ == 'list'):
                    body = body[0]

                build_id = body['id'] if ('id' in body.keys()) else None
                if (build_id == None):
                    self._mh.demsg('htk_on_error', self._mh._trn.msg(
                        'track_error', body['code'], body['message']), self._mh.fromhere())
                    return False, None

            params = {'devKey': self._dev_key,
                      'testplanid': plan_id, 'buildid': build_id}
            recs = self._client.call_method(
                'tl.getTestCasesForTestPlan', params)

            records_new = []
            if (len(recs) > 0):

                if (recs.__class__.__name__ == 'list'):
                    self._mh.demsg('htk_on_error', self._mh._trn.msg(
                        'track_error', recs[0]['code'], recs[0]['message']), self._mh.fromhere())
                    return False, None

                records = []
                for key in sorted(recs.keys()):
                    records.append(recs[key][0])
                for record in records:
                    record_new = {}
                    for key, value in record.items():
                        if (fields == None or key in fields):
                            record_new[key] = value

                    if (record_new != {}):
                        records_new.append(record_new)

        if (recs != None):
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('track_folder_read', len(records_new)),
                          self._mh.fromhere())
            ev = event.Event('track_after_read_plan')
            self._mh.fire_event(ev)
            return True, records_new
        else:
            return False, None

    def create_test_plan(self, name, notes=None):
        """Method creates test plan

        Args: 
           name (str): plan name
           notes (str): plan notes

        Returns:
           int: plan id

        Raises:
           event: track_before_create
           event: track_after_create

        """

        message = 'name:{0}, notes:{1}'.format(name, notes)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_creating', 'test_plan', message), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return None

        ev = event.Event('track_before_create', name, notes)
        if (self._mh.fire_event(ev) > 0):
            name = ev.argv(0)
            notes = ev.argv(1)

        if (ev.will_run_default()):
            params = {'devKey': self._dev_key, 'testprojectname':
                      self._project, 'testplanname': name, 'notes': notes}
            body = self._client.call_method('tl.createTestPlan', params)

        id = None
        if (body != None):
            if (body.__class__.__name__ == 'list'):
                body = body[0]

            id = int(body['id']) if (
                'id' in body.keys() and int(body['id']) > 0) else None
            if (id != None):
                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_created', id), self._mh.fromhere())
                ev = event.Event('track_after_create')
                self._mh.fire_event(ev)
            else:
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_error', body['code'], body['message']), self._mh.fromhere())

        return id

    def create_build(self, plan, name, notes=None):
        """Method creates build

        Args: 
           plan (int): plan id
           name (str): build name
           notes (str): build notes

        Returns:
           int: build id

        Raises:
           event: track_before_create
           event: track_after_create

        """

        message = 'plan:{0}, name:{1}, notes:{1}'.format(plan, name, notes)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_creating', 'build', message), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return None

        ev = event.Event('track_before_create', plan, name, notes)
        if (self._mh.fire_event(ev) > 0):
            plan = ev.argv(0)
            name = ev.argv(1)
            notes = ev.argv(2)

        if (ev.will_run_default()):
            params = {'devKey': self._dev_key, 'testplanid': plan,
                      'buildname': name, 'buildnotes': notes}
            body = self._client.call_method('tl.createBuild', params)

        id = None
        if (body != None):
            if (body.__class__.__name__ == 'list'):
                body = body[0]

            id = int(body['id']) if (
                'id' in body.keys() and int(body['id']) > 0) else None
            if (id != None):
                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_created', id), self._mh.fromhere())
                ev = event.Event('track_after_create')
                self._mh.fire_event(ev)
            else:
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_error', body['code'], body['message']), self._mh.fromhere())

        return id

    def read_test(self, id, fields=None):
        """Method reads test

        Args: 
           id (int): test id
           fields (list): fields to be returned default all

        Returns:
           tuple: result (bool), test (dict)

        Raises:
           event: track_before_read
           event: track_after_read

        """

        message = 'id:{0}, fields:{1}'.format(id, fields)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_reading', 'test', message), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False, None

        ev = event.Event('track_before_read', id, fields)
        if (self._mh.fire_event(ev) > 0):
            id = ev.argv(0)
            fields = ev.argv(1)

        if (ev.will_run_default()):
            params = {'devKey': self._dev_key, 'testcaseid': id}
            body = self._client.call_method('tl.getTestCase', params)

        result, test = False, None
        if (body != None):
            if (body.__class__.__name__ == 'list'):
                body = body[0]

            id = body['id'] if (
                'id' in body.keys() and int(body['id']) > 0) else None
            if (id != None):
                test = {}
                for key, value in body.items():
                    if (fields == None or key in fields):
                        test[key] = value

                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_read', 1), self._mh.fromhere())
                ev = event.Event('track_after_read')
                self._mh.fire_event(ev)
                result = True
            else:
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_error', body['code'], body['message']), self._mh.fromhere())

        return result, test

    def create_test(self, path, params={}, steps=[]):
        """Method creates test

        Args: 
           path (str): suite path
           params (dict): params, key - field name, value - field value
           steps (list): list of dict, key - field name, value - field value

        Returns:
           int: test id

        Raises:
           event: track_before_create
           event: track_after_create

        """

        message = 'path:{0}, params:{1}, steps:{2}'.format(path, params, steps)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_creating', 'test', message), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return None

        if (self._default_values != None):
            for key, value in self._default_values.items():
                if (key not in params):
                    params[key] = value

        ev = event.Event('track_before_create', path, params, steps)
        if (self._mh.fire_event(ev) > 0):
            path = ev.argv(0)
            params = ev.argv(1)
            steps = ev.argv(2)

        if (ev.will_run_default()):
            suite = self._get_suite(path)
            if (suite == None):
                return None

            for i in range(0, len(steps)):
                if ('step_number' not in steps[i].keys()):
                    steps[i]['step_number'] = i + 1

            params['devKey'] = self._dev_key
            params['testprojectid'] = self._project_id
            params['testsuiteid'] = suite
            params['steps'] = steps
            body = self._client.call_method('tl.createTestCase', params)

        id = None
        if (body != None):
            if (body.__class__.__name__ == 'list'):
                body = body[0]

            id = int(body['id']) if (
                'id' in body.keys() and int(body['id']) > 0) else None
            if (id != None):
                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_created', id), self._mh.fromhere())
                ev = event.Event('track_after_create')
                self._mh.fire_event(ev)
            else:
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_error', body['code'], body['message']), self._mh.fromhere())

        return id

    def add_test_to_plan(self, test, plan=None, plan_id=None):
        """Method adds test to plan

        Args:            
           test (int): test id
           plan (str): plan name
           plan_id (int): plan_id

        Returns:
           bool: result

        Raises:
           event: track_before_update
           event: track_after_update

        """

        message = 'plan:{0}, plan_id:{1}'.format(plan, plan_id)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_updating', 'test_plan', test, message), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False

        ev = event.Event('track_before_update', test, plan, plan_id)
        if (self._mh.fire_event(ev) > 0):
            test = ev.argv(0)
            plan = ev.argv(1)
            plan_id = ev.argv(2)

        if (ev.will_run_default()):

            if (plan != None):
                params = {
                    'devKey': self._dev_key, 'testprojectname': self._project, 'testplanname': plan}
                body = self._client.call_method('tl.getTestPlanByName', params)

                if (body.__class__.__name__ == 'list'):
                    body = body[0]

                plan_id = body['id'] if ('id' in body.keys()) else None
                if (plan_id == None):
                    self._mh.demsg('htk_on_error', self._mh._trn.msg(
                        'track_error', body['code'], body['message']), self._mh.fromhere())
                    return False, None

            params = {'devKey': self._dev_key, 'testprojectid':
                      self._project_id, 'testplanid': plan_id, 'testcaseid': test}
            res, test_detail = self.read_test(test)
            if (res):
                params['version'] = int(test_detail['version'])
            body = self._client.call_method('tl.addTestCaseToTestPlan', params)

        result = False
        if (body != None):
            if (body.__class__.__name__ == 'list'):
                body = body[0]

            status = body['status'] if ('status' in body.keys()) else None
            if (status != None):
                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_updated', test), self._mh.fromhere())
                ev = event.Event('track_after_update')
                self._mh.fire_event(ev)
                result = True
            else:
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_error', body['code'], body['message']), self._mh.fromhere())

        return result

    def update_test_execution(self, test, status, notes=None, plan=None, plan_id=None, build_id=None):
        """Method updates test execution

        Args:
           test (int): test id
           status (str): status, p|f|b (passed|failed|blocked)
           notes (str): execution notes                
           plan (str): plan name, will be translated to id
           plan_id (int): plan id 
           build_id (int): build id, latest build will be used if not specified   

        Returns:
           bool: result   

        """

        message = 'status:{0}, notes:{1}, plan:{2}, plan_id:{3}, build_id:{4}'.format(
            status, notes, plan, plan_id, build_id)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_updating', 'test', test, message), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False

        ev = event.Event(
            'track_before_update', test, status, notes, plan, plan_id, build_id)
        if (self._mh.fire_event(ev) > 0):
            test = ev.argv(0)
            status = ev.argv(1)
            notes = ev.argv(2)
            plan = ev.argv(3)
            plan_id = ev.argv(4)
            build_id = ev.argv(5)

        if (ev.will_run_default()):

            if (plan != None):
                params = {
                    'devKey': self._dev_key, 'testprojectname': self._project, 'testplanname': plan}
                body = self._client.call_method('tl.getTestPlanByName', params)

                if (body.__class__.__name__ == 'list'):
                    body = body[0]

                plan_id = body['id'] if ('id' in body.keys()) else None
                if (plan_id == None):
                    self._mh.demsg('htk_on_error', self._mh._trn.msg(
                        'track_error', body['code'], body['message']), self._mh.fromhere())
                    return False

            if (build_id == None):
                params = {'devKey': self._dev_key, 'testplanid': plan_id}
                body = self._client.call_method(
                    'tl.getLatestBuildForTestPlan', params)
                if (body.__class__.__name__ == 'list'):
                    body = body[0]

                build_id = body['id'] if ('id' in body.keys()) else None
                if (build_id == None):
                    self._mh.demsg('htk_on_error', self._mh._trn.msg(
                        'track_error', body['code'], body['message']), self._mh.fromhere())
                    return False

            params = {'devKey': self._dev_key, 'testplanid': plan_id, 'buildid':
                      build_id, 'testcaseid': test, 'status': status, 'notes': notes}
            body = self._client.call_method('tl.reportTCResult', params)

        result = False
        if (body != None):
            if (body.__class__.__name__ == 'list'):
                body = body[0]

            status = body['status'] if ('status' in body.keys()) else None
            if (status != None):
                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_updated', test), self._mh.fromhere())
                ev = event.Event('track_after_update')
                self._mh.fire_event(ev)
                result = True
            else:
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_error', body['code'], body['message']), self._mh.fromhere())

        return result

    def _get_suite(self, path):
        """Method gets suite from hierarchical path

        Args: 
           path (str): suite path, Suite1/Suite2/...    

        Returns:
           int: suite id

        """

        folders = path.split('/')
        cnt = len(folders)

        found = False
        id = None
        for i in range(0, cnt):
            if (i == 0):
                params = {
                    'devKey': self._dev_key, 'testprojectid': self._project_id}
                recs = self._client.call_method(
                    'tl.getFirstLevelTestSuitesForTestProject', params)
            else:
                params = {'devKey': self._dev_key, 'testsuiteid': id}
                recs = self._client.call_method(
                    'tl.getTestSuitesForTestSuite', params)

            found = False
            if (recs != None):
                if (recs.__class__.__name__ == 'dict'):
                    recs = [recs] if (
                        list(recs.values())[0].__class__.__name__ != 'dict') else recs.values()
                for rec in recs:
                    if (rec['name'] == folders[i]):
                        id = rec['id']
                        found = True
                        break

            if (not found):
                self._mh.demsg('htk_on_error', self._mh._trn.msg('track_unknown_folder', folders[i]),
                              self._mh.fromhere())
                return None

        return id
