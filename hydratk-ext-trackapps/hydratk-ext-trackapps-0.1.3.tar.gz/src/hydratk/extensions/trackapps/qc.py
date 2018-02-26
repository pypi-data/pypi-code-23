# -*- coding: utf-8 -*-
"""Client for HP Quality Center

.. module:: trackapps.qc
   :platform: Unix
   :synopsis: Client for HP Quality Center
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
track_before_delete
track_after_delete
track_before_read_folder
track_after_read_folder
track_before_read_set
track_after_read_set

"""

from hydratk.core.masterhead import MasterHead
from hydratk.core import event
from hydratk.lib.network.rest.client import RESTClient
from lxml.etree import Element, SubElement, tostring
from sys import version_info

config = {
    'sign_in': '/authentication-point/authenticate',
    'auth': '/rest/site-session',
    'sign_out': '/authentication-point/logout',
    'rest': '/rest/domains/{0}/projects/{1}/{2}s',
    'entities': ['defect', 'test-folder', 'test', 'test-set-folder', 'test-set', 'test-instance']
}


class Client(object):
    """Class Client
    """

    _mh = None
    _client = None
    _url = None
    _user = None
    _passw = None
    _domain = None
    _project = None
    _cookie = None
    _return_fields = {}
    _default_values = {}
    _is_connected = None

    def __init__(self):
        """Class constructor

        Called when the object is initialized  

        Args:
           none 

        """

        self._mh = MasterHead.get_head()
        self._client = RESTClient()

        cfg = self._mh.cfg['Extensions']['TrackApps']['qc']
        if ('return_fields' in cfg and cfg['return_fields'] != None):
            self._return_fields = cfg['return_fields']
            if (self._return_fields.__class__.__name__ == 'dict'):
                for key, value in cfg['return_fields'].items():
                    if (value != None):
                        self._return_fields[key] = value.split(',')
        if ('default_values' in cfg and cfg['default_values'] != None):
            default_values = {}
            for entity, expr in cfg['default_values'].items():
                default_values[entity] = {}
                if (expr != None):
                    params = expr.split('#')
                    for param in params:
                        conf = param.split('%')
                        default_values[entity][conf[0]] = conf[1]
            self._default_values = default_values
        if ('url' in cfg and cfg['url'] != None):
            self._url = cfg['url']
        if ('user' in cfg and cfg['user'] != None):
            self._user = cfg['user']
        if ('passw' in cfg and cfg['passw'] != None):
            self._passw = cfg['passw']
        if ('domain' in cfg and cfg['domain'] != None):
            self._domain = cfg['domain']
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
    def user(self):
        """ user property getter """

        return self._user

    @property
    def passw(self):
        """ passw property getter """

        return self._passw

    @property
    def domain(self):
        """ domain property getter """

        return self._domain

    @property
    def project(self):
        """ project property getter """

        return self._project

    @property
    def cookie(self):
        """ cookie property getter """

        return self._cookie

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

    def connect(self, url=None, user=None, passw=None, domain=None, project=None):
        """Method connects to QC

        Args:    
           url (str): URL        
           user (str): username
           passw (str): password
           domain (str): QC domain
           project (str): QC project

        Returns:
           bool: result

        Raises:
           event: track_before_connect
           event: track_after_connect

        """

        message = 'url:{0}, user:{1}, passw:{2}, domain:{3}, project:{4}'.format(
            url, user, passw, domain, project)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_connecting', message), self._mh.fromhere())

        if (url == None):
            url = self._url
        if (user == None):
            user = self._user
        if (passw == None):
            passw = self._passw
        if (domain == None):
            domain = self._domain
        if (project == None):
            project = self._project

        ev = event.Event(
            'track_before_connect', url, user, passw, domain, project)
        if (self._mh.fire_event(ev) > 0):
            url = ev.argv(0)
            user = ev.argv(1)
            passw = ev.argv(2)
            domain = ev.argv(3)
            project = ev.argv(4)

        if (ev.will_run_default()):
            self._url = url
            self._user = user
            self._passw = passw
            self._domain = domain
            self._project = project

            url = self._url + config['sign_in']
            res, body = self._client.send_request(
                url, user=self._user, passw=self._passw, method='POST')
            if (res == 200):
                url, cookie = self._url + \
                    config['auth'], self._client.get_header('set-cookie')
                headers = {'Cookie': cookie}
                res, body = self._client.send_request(
                    url, user=self._user, passw=self._passw, method='POST', headers=headers)

        result = False
        if (res in [200, 201]):

            self._cookie = '{0}, {1}'.format(
                cookie, self._client.get_header('set-cookie'))
            if (self._cookie != None):
                self._is_connected = True
                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_connected'), self._mh.fromhere())
                ev = event.Event('track_after_connect')
                self._mh.fire_event(ev)
                result = True
            else:
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_missing_cookie'), self._mh.fromhere())
        else:
            error = body.Title if (hasattr(body, 'Title')) else body
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_error', res, error), self._mh.fromhere())

        return result

    def disconnect(self):
        """Method disconnects from QC

        Args:   
           none 

        Returns:
           bool: result

        """

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_disconnecting'), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False

        url = self._url + config['sign_out']
        res, body = self._client.send_request(
            url, method='POST', headers={'Cookie': self._cookie})

        result = False
        if (res == 200):
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_disconnected'), self._mh.fromhere())
            self._cookie = None
            self._is_connected = False
            result = True
        else:
            error = body.Title if (hasattr(body, 'Title')) else body
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_error', res, error), self._mh.fromhere())

        return result

    def read(self, id=None, entity='defect', fields=None, query=None, order_by=None, limit=None, offset=None):
        """Method reads records

        Args: 
           id (int): record id
           entity (str): entity type    
           fields (list): fields to be returned, default all
           query (str): record query
           order_by (dict): record ordering, key - field, value - direction asc|desc 
           limit (int): record count    
           offset (int): record offset

        Returns:
           tuple: result (bool), records (list of dictionary)

        Raises:
           event: track_before_read
           event: track_after_read

        """

        if (entity not in config['entities']):
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_unknown_entity', entity), self._mh.fromhere())
            return (False, None)

        message = 'entity:{0}, id:{1}, fields:{2}, query:{3}, order_by:{4}, limit:{5}, offset:{6}'.format(
            entity, id, fields, query, order_by, limit, offset)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_reading', message), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False, None

        if (fields == None and entity in self._return_fields and self._return_fields[entity] != None):
            fields = self._return_fields[entity]

        ev = event.Event(
            'track_before_read', entity, id, fields, query, order_by, limit, offset)
        if (self._mh.fire_event(ev) > 0):
            entity = ev.argv(0)
            id = ev.argv(1)
            fields = ev.argv(2)
            query = ev.argv(3)
            order_by = ev.argv(4)
            limit = ev.argv(5)
            offset = ev.argv(6)

        if (ev.will_run_default()):

            params = {}
            if (fields != None and len(fields) > 0):
                param = ""
                for field in fields:
                    param += field + ','
                params['fields'] = param[:-1]
            if (query != None):
                params['query'] = query
            if (id != None):
                params['query'] = '{ID[%s]}' % id
            if (order_by != None and len(order_by.keys()) > 0):
                param = ""
                for field, direction in order_by.items():
                    if (direction == 'asc'):
                        param += '+' + field + ','
                    elif (direction == 'desc'):
                        param += '-' + field + ','
                params['order-by'] = param[:-1]
            if (limit != None):
                params['limit'] = limit
            if (offset != None):
                params['offset'] = offset

            url = self._url + \
                config['rest'].format(self._domain, self._project, entity)
            headers = {'Cookie': self._cookie}
            res, body = self._client.send_request(url, method='GET', headers=headers, params=params,
                                                  content_type='xml')

        result = False
        records = None
        if (res == 200):
            records = []
            if (int(body.get('TotalResults')) > 0):
                for ent in body.Entity:
                    record = {}
                    for field in ent.Fields.Field:
                        key = field.get('Name')
                        value = field.Value if (
                            hasattr(field, 'Value')) else None
                        if (fields == None or key in fields):
                            record[key] = value
                    records.append(record)

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_read', len(records)), self._mh.fromhere())
            ev = event.Event('track_after_read')
            self._mh.fire_event(ev)
            result = True
        else:
            error = body.Title if (hasattr(body, 'Title')) else body
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_error', res, error), self._mh.fromhere())

        return (result, records)

    def create(self, entity='defect', params={}):
        """Method creates record

        Args: 
           entity (str): entity type
           params (dict): record content, key - field name, value - field value

        Returns:
           int: record id

        Raises:
           event: track_before_create
           event: track_after_create

        """

        if (entity not in config['entities']):
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_unknown_entity', entity), self._mh.fromhere())
            return None

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_creating', entity, params), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return None

        if (entity in self._default_values and self._default_values[entity] != None):
            for key, value in self._default_values[entity].items():
                if (key not in params):
                    params[key] = value

        ev = event.Event('track_before_create', entity, params)
        if (self._mh.fire_event(ev) > 0):
            entity = ev.argv(0)
            params = ev.argv(1)

        if (ev.will_run_default()):

            root = Element('Entity')
            root.set('Type', entity)
            el_fields = SubElement(root, 'Fields')
            for key, value in params.items():
                elem = SubElement(el_fields, 'Field')
                elem.set('Name', key)
                SubElement(elem, 'Value').text = str(value).decode(
                    'utf8') if (version_info[0] == 2) else str(value)
            body = tostring(root)

            url = self._url + \
                config['rest'].format(self._domain, self._project, entity)
            headers = {'Cookie': self._cookie}
            res, body = self._client.send_request(url, method='POST', headers=headers, body=body,
                                                  content_type='xml')
        id = None
        if (res in (200, 201)):
            id = int(
                body.xpath("//Entity/Fields/Field[@Name='id']/Value/text()")[0])
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_created', id), self._mh.fromhere())
            ev = event.Event('track_after_create')
            self._mh.fire_event(ev)
        else:
            error = body.Title if (hasattr(body, 'Title')) else body
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_error', res, error), self._mh.fromhere())

        return id

    def update(self, id, entity='defect', params={}):
        """Method updates record

        Args: 
           id (int): entity id
           entity (str): entity type         
           params (dict): record content, key - field name, value - field value 

        Returns:
           bool: result

        Raises:
           event: track_before_update
           event: track_after_update

        """

        if (entity not in config['entities']):
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_unknown_entity', entity), self._mh.fromhere())
            return False

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_updating', entity, id, params), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False

        ev = event.Event('track_before_update', entity, id, params)
        if (self._mh.fire_event(ev) > 0):
            entity = ev.argv(0)
            id = ev.argv(1)
            params = ev.argv(2)

        if (ev.will_run_default()):

            root = Element('Entity')
            root.set('Type', entity)
            el_fields = SubElement(root, 'Fields')
            for key, value in params.items():
                elem = SubElement(el_fields, 'Field')
                elem.set('Name', key)
                SubElement(elem, 'Value').text = str(value).decode(
                    'utf8') if (version_info[0] == 2) else str(value)
            body = tostring(root)

            url = self._url + \
                config['rest'].format(
                    self._domain, self._project, entity) + '/' + str(id)
            headers = {'Cookie': self._cookie}
            res, body = self._client.send_request(url, method='PUT', headers=headers, body=body,
                                                  content_type='xml')
        result = False
        if (res == 200):
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_updated', id), self._mh.fromhere())
            ev = event.Event('track_after_update')
            self._mh.fire_event(ev)
            result = True
        else:
            error = body.Title if (hasattr(body, 'Title')) else body
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_error', res, error), self._mh.fromhere())

        return result

    def delete(self, id, entity='defect'):
        """Method deletes record

        Args: 
           id (int): entity id
           entity (str): entity type          

        Returns:
           bool: result

        Raises:
           event: track_before_delete
           event: track_after_delete

        """

        if (entity not in config['entities']):
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_unknown_entity', entity), self._mh.fromhere())
            return False

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_deleting', entity, id), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False

        ev = event.Event('track_before_delete', entity, id)
        if (self._mh.fire_event(ev) > 0):
            entity = ev.argv(0)
            id = ev.argv(1)

        if (ev.will_run_default()):

            url = self._url + \
                config['rest'].format(
                    self._domain, self._project, entity) + '/' + str(id)
            headers = {'Cookie': self._cookie}
            res, body = self._client.send_request(
                url, method='DELETE', headers=headers, content_type='xml')

        result = False
        if (res == 200):
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_deleted', id), self._mh.fromhere())
            ev = event.Event('track_after_delete')
            self._mh.fire_event(ev)
            result = True
        else:
            error = body.Title if (hasattr(body, 'Title')) else body
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_error', res, error), self._mh.fromhere())

        return result

    def read_test_folder(self, path, entity='test-folder'):
        """Method reads tests under test folder

        Args: 
           path (str): folder path   
           entity (str): entity type, test-folder|test-set-folder

        Returns:
           tuple: result (bool), records (dict), key - test folder, value - list of tests

        Raises:
           event: track_before_read_folder
           event: track_after_read_folder

        """

        if (entity not in ['test-folder', 'test-set-folder']):
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_unknown_entity', entity), self._mh.fromhere())
            return (False, None)

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('track_reading_folder', path, entity),
                      self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False, None

        ev = event.Event('track_before_read_folder', path, entity)
        if (self._mh.fire_event(ev) > 0):
            path = ev.argv(0)
            entity = ev.argv(1)

        if (ev.will_run_default()):

            folder = self._get_folder(path, entity)
            if (folder == None):
                return (False, None)

            hier_path = folder['hierarchical-path']
            if (hier_path != None):
                fields = ['id', 'name', 'parent-id']
                query = '{hierarchical-path[%s*]}' % hier_path
                res, folders = self.read(
                    entity=entity, fields=fields, query=query)

                top_id = folder['id']
                names_new = []
                for i in range(0, len(folders)):

                    if (folders[i]['id'] == top_id):
                        names_new.append(path)
                    else:
                        parent_id = folders[i]['parent-id']
                        name = folders[i]['name']
                        while (parent_id != top_id):

                            j = 0
                            while (folders[j]['id'] != parent_id):
                                j += 1
                            parent_id = folders[j]['parent-id']
                            name = '{0}/{1}'.format(folders[j]['name'], name)

                        names_new.append('{0}/{1}'.format(path, name))

                for i in range(0, len(folders)):
                    folders[i]['name'] = names_new[i]

        if (res):
            tests = {}
            cnt = 0
            entity = 'test' if (entity == 'test-folder') else 'test-set'
            fields = None if (entity == 'test-folder') else ['id', 'name']
            for rec in folders:
                query = '{parent-id[%d]}' % rec['id']
                res, records = self.read(
                    entity=entity, fields=fields, query=query)
                if (res):
                    tests[rec['name']] = records
                    cnt += len(records)

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_folder_read', cnt), self._mh.fromhere())
            ev = event.Event('track_after_read_folder')
            self._mh.fire_event(ev)

            return (True, tests)

        else:
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_missing_hier', folder['name']), self._mh.fromhere())
            return (False, None)

    def create_test_folder(self, path, name, entity='test-folder'):
        """Method creates test folder on path

        Args: 
           path (str): folder path
           name (str): folder name
           entity (str): entity type, test-folder|test-set-folder

        Returns:
           int: folder id

        """

        if (entity not in ['test-folder', 'test-set-folder']):
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_unknown_entity', entity), self._mh.fromhere())
            return None

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return None

        folder = self._get_folder(path, entity)
        if (folder == None):
            return None

        params = {'name': name, 'parent-id': folder['id']}
        return self.create(entity, params)

    def read_test_set(self, id):
        """Method reads tests under test set

        Args: 
           id (int): test set id

        Returns:
           tuple: result (bool), tests (list of dict)

        Raises:
           track_before_read_set
           track_after_read_set

        """

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('track_reading_set', id),
                      self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False, None

        ev = event.Event('track_before_read_set', id)
        if (self._mh.fire_event(ev) > 0):
            id = ev.argv(0)

        if (ev.will_run_default()):
            fields = ['test-id', 'status', 'exec-date', 'actual-tester']
            query = '{cycle-id[%d]}' % id
            res, tests = self.read(
                entity='test-instance', fields=fields, query=query)

        if (res):
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_set_read', len(tests)), self._mh.fromhere())
            ev = event.Event('track_after_read_set')
            self._mh.fire_event(ev)

            return (True, tests)
        else:
            return (False, None)

    def create_test_set(self, path, params={}):
        """Method creates test set on path

        Args: 
           path (str): folder path
           params (dict): test content, key - field name, value - field value  

        Returns:
           int: test set id

        """

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return None

        folder = self._get_folder(path, 'test-set-folder')
        if (folder == None):
            return None

        params['parent-id'] = folder['id']
        return self.create('test-set', params)

    def create_test(self, path, params={}):
        """Method creates test on path

        Args: 
           path (str): folder path
           params (dict): test content, key - field name, value - field value    

        Returns:
           int: test id

        """

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return None

        folder = self._get_folder(path)
        if (folder == None):
            return None

        params['parent-id'] = folder['id']
        return self.create('test', params)

    def _get_folder(self, path, entity='test-folder'):
        """Method gets folder from hierarchical path

        Args: 
           path (str): folder path, Folder1/Folder2/...    
           entity (str): entity type, test-folder|test-set-folder

        Returns:
           dict

        """

        folders = path.split('/')
        fields = ['id', 'name', 'hierarchical-path']
        parent_id = 0

        if (folders[0] == 'Root'):
            folders = folders[1:]

        cnt = len(folders)
        for i in range(0, cnt):
            query = '{parent-id[%d]}' % parent_id
            res, records = self.read(entity=entity, fields=fields, query=query)

            if (res):
                found = False
                j = 0
                while (not found and j < len(records)):
                    record = records[j]
                    if (record['name'] == folders[i]):
                        parent_id = record['id']
                        found = True
                    j += 1

            if (not found):
                self._mh.demsg('htk_on_error', self._mh._trn.msg('track_unknown_folder', folders[i]),
                              self._mh.fromhere())
                return None

        return record
