# -*- coding: utf-8 -*-
"""Client for Jira

.. module:: trackapps.jira
   :platform: Unix
   :synopsis: Client for Jira
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

"""

from hydratk.core.masterhead import MasterHead
from hydratk.core import event
from hydratk.lib.network.rest.client import RESTClient
from simplejson import dumps

config = {
    'session': '/rest/auth/1/session',
    'search': '/rest/api/2/search',
    'issue': '/rest/api/2/issue'
}


class Client(object):
    """Class Client
    """

    _mh = None
    _client = None
    _url = None
    _user = None
    _passw = None
    _project = None
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
        self._client = RESTClient()

        cfg = self._mh.cfg['Extensions']['TrackApps']['jira']
        if ('return_fields' in cfg and cfg['return_fields'] != None):
            self._return_fields = cfg['return_fields'].split(',')
        if ('default_values' in cfg and cfg['default_values'] != None):
            self._default_values = cfg['default_values']
        if ('url' in cfg and cfg['url'] != None):
            self._url = cfg['url']
        if ('user' in cfg and cfg['user'] != None):
            self._user = cfg['user']
        if ('passw' in cfg and cfg['passw'] != None):
            self._passw = cfg['passw']
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
    def project(self):
        """ project property getter """

        return self._project

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

    def connect(self, url=None, user=None, passw=None, project=None):
        """Method connects to Jira

        Args:    
           url (str): URL        
           user (str): username
           passw (str): password
           project (str): project

        Returns:
           bool: result

        Raises:
           event: track_before_connect
           event: track_after_connect

        """

        message = 'url:{0}, user:{1}, passw:{2}, project:{3}'.format(
            url, user, passw, project)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_connecting', message), self._mh.fromhere())

        if (url == None):
            url = self._url
        if (user == None):
            user = self._user
        if (passw == None):
            passw = self._passw
        if (project == None):
            project = self._project

        ev = event.Event('track_before_connect', url, user, passw, project)
        if (self._mh.fire_event(ev) > 0):
            url = ev.argv(0)
            user = ev.argv(1)
            passw = ev.argv(2)
            project = ev.argv(3)

        if (ev.will_run_default()):
            self._url = url
            self._user = user
            self._passw = passw
            self._project = project

            url = self._url + config['session']
            body = {'username': self._user, 'password': self._passw}
            res, body = self._client.send_request(url, method='POST', headers={'Accept': 'application/json'},
                                                  body=dumps(body), content_type='json')

        result = False
        if (res == 200):
            self._is_connected = True
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_connected'), self._mh.fromhere())
            ev = event.Event('track_after_connect')
            self._mh.fire_event(ev)
            result = True
        else:
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_error', res, body), self._mh.fromhere())

        return result

    def read(self, id=None, fields=None, query=None, limit=None, offset=None):
        """Method reads records

        Args: 
           id (int): record id         
           fields (list): fields to be returned, default all
           query (str): record query, see Jira doc
           limit (int): record count    
           offset (int): record offset

        Returns:
           tuple: result (bool), records (list of dictionary)

        Raises:
           event: track_before_read
           event: track_after_read

        """

        message = 'id:{0}, fields:{1}, query:{2}, limit:{3}, offset:{4}'.format(
            id, fields, query, limit, offset)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_reading', message), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False, None

        if (fields == None and self._return_fields != None):
            fields = self._return_fields
        ev = event.Event('track_before_read', id, fields, query, limit, offset)
        if (self._mh.fire_event(ev) > 0):
            id = ev.argv(0)
            fields = ev.argv(1)
            query = ev.argv(2)
            limit = ev.argv(3)
            offset = ev.argv(4)

        if (ev.will_run_default()):

            body = {}
            if (id != None):
                body['jql'] = 'key={0}-{1}'.format(self._project, id)
            else:
                body['jql'] = 'project=' + self._project
            if (fields != None and len(fields) > 0):
                fields_new = []
                for field in fields:
                    fields_new.append(field)
                body['fields'] = fields_new
            if (query != None):
                body['jql'] += ' and ' + query
            if (limit != None):
                body['maxResults'] = limit
            if (offset != None):
                body['startAt'] = offset
            body = dumps(body)

            url = self._url + config['search']
            res, body = self._client.send_request(url, method='POST', user=self._user, passw=self._passw,
                                                  headers={'Accept': 'application/json'}, body=body, content_type='json')

            result = False
            records = None
            if (res == 200):
                cnt2 = len(body['issues'])
                cnt = body['total'] if (body['total'] == cnt2) else cnt2
                records = []
                for i in range(0, cnt):
                    record = {}
                    if (fields == None or 'id' in fields):
                        record['id'] = int(
                            body['issues'][i]['key'].split('-')[-1])
                    for key, value in body['issues'][i]['fields'].items():
                        if (fields == None or key in fields):
                            record[key] = value
                    if (record != {}):
                        records.append(record)

                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_read', cnt), self._mh.fromhere())
                ev = event.Event('track_after_read')
                self._mh.fire_event(ev)
                result = True
            else:
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_error', res, body), self._mh.fromhere())

            return (result, records)

    def create(self, params={}):
        """Method creates record

        Args: 
           params (dict): record content, key - field name, value - field value

        Returns:
           int: record id

        Raises:
           event: track_before_create
           event: track_after_create

        """

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_creating', 'issue', params), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return None

        if (self._default_values != {}):
            for key, value in self._default_values.items():
                if (key not in params):
                    params[key] = value

        ev = event.Event('track_before_create', params)
        if (self._mh.fire_event(ev) > 0):
            params = ev.argv(0)

        if (ev.will_run_default()):

            root = {'fields': {}}
            for key, value in params.items():
                root['fields'][key] = value
            if ('project' not in root['fields']):
                root['fields']['project'] = {'key': self._project}
            if ('issuetype' not in root['fields']):
                root['fields']['issuetype'] = {'name': 'Bug'}
            body = dumps(root)

            url = self._url + config['issue']
            res, body = self._client.send_request(url, method='POST', user=self._user, passw=self._passw,
                                                  headers={'Accept': 'application/json'}, body=body, content_type='json')

        id = None
        if (res in (200, 201)):
            id = int(body['key'].split('-')[1])
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_created', id), self._mh.fromhere())
            ev = event.Event('track_after_create')
            self._mh.fire_event(ev)
        else:
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_error', res, body), self._mh.fromhere())

        return id

    def update(self, id, params={}):
        """Method updates record

        Args: 
           id (int): record id
           params (dict): record content, key - field name, value - field value

        Returns:
           bool: result

        Raises:
           event: track_before_update
           event: track_after_update

        """

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('track_updating', 'issue', id, params),
                      self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False

        ev = event.Event('track_before_update', id, params)
        if (self._mh.fire_event(ev) > 0):
            id = ev.argv(0)
            params = ev.argv(1)

        if (ev.will_run_default()):

            root = {'fields': {}}
            for key, value in params.items():
                root['fields'][key] = value
            body = dumps(root)

            url = self._url + config['issue'] + \
                '/{0}-{1}'.format(self._project, id)
            res, body = self._client.send_request(url, method='POST', user=self._user, passw=self._passw,
                                                  headers={'Accept': 'application/json'}, body=body, content_type='json')

        result = False
        if (res in (200, 204)):
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_updated', id), self._mh.fromhere())
            ev = event.Event('track_after_update')
            self._mh.fire_event(ev)
            result = True
        else:
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_error', res, body), self._mh.fromhere())

        return result
