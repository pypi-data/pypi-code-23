# -*- coding: utf-8 -*-
"""Client for Bugzilla

.. module:: trackapps.bugzilla
   :platform: Unix
   :synopsis: Client for Bugzilla
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
    'login': '/rest.cgi/login',
    'logout': '/rest.cgi/logout',
    'rest': '/rest.cgi/bug'
}


class Client(object):
    """Class Client
    """

    _mh = None
    _client = None
    _url = None
    _user = None
    _passw = None
    _token = None
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

        cfg = self._mh.cfg['Extensions']['TrackApps']['bugzilla']
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
    def token(self):
        """ token property getter """

        return self._token

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
        """ is_conncted property getter """

        return self._is_connected

    def connect(self, url=None, user=None, passw=None):
        """Method connects to Bugzilla

        Args:    
           url (str): URL        
           user (str): username
           passw (str): password

        Returns:
           bool: result

        Raises:
           event: track_before_connect
           event: track_after_connect

        """

        message = 'url:{0}, user:{1}, passw:{2}'.format(url, user, passw)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_connecting', message), self._mh.fromhere())

        if (url == None):
            url = self._url
        if (user == None):
            user = self._user
        if (passw == None):
            passw = self._passw

        ev = event.Event('track_before_connect', url, user, passw)
        if (self._mh.fire_event(ev) > 0):
            url = ev.argv(0)
            user = ev.argv(1)
            passw = ev.argv(2)

        if (ev.will_run_default()):
            self._url = url
            self._user = user
            self._passw = passw

            url = self._url + config['login']
            params = {'login': self._user, 'password': self._passw}
            res, body = self._client.send_request(url, method='GET', headers={'Accept': 'application/json'},
                                                  params=params, content_type='json')

        result = False
        if (res == 200):
            self._token = body['token']
            if (self._token != None):
                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_connected'), self._mh.fromhere())
                ev = event.Event('track_after_connect')
                self._mh.fire_event(ev)
                self._is_connected = True
                result = True
            else:
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_missing_token'), self._mh.fromhere())
        else:
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_error', res, body), self._mh.fromhere())

        return result

    def disconnect(self):
        """Method disconnects from Bugzilla

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

        url = self._url + config['logout']
        res, body = self._client.send_request(
            url, method='GET', params={'token': self._token})

        result = False
        if (res == 200):
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_disconnected'), self._mh.fromhere())
            self._token = None
            self._is_connected = False
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
           query (dict): record query, see Bugzilla doc
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

            params = {}
            if (query != None):
                for key, val in query.items():
                    params[key] = val
            if (id != None):
                params['id'] = id
            if (limit != None):
                params['limit'] = limit
            if (offset != None):
                params['offset'] = offset

            url = self._url + config['rest']
            params['token'] = self._token
            res, body = self._client.send_request(url, method='GET', headers={'Accept': 'application/json'},
                                                  params=params, content_type='json')
            result = False
            records = None
            if (res == 200):

                cnt = len(body['bugs'])
                records = []
                for i in range(0, cnt):
                    record = {}
                    for key, value in body['bugs'][i].items():
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
            'track_creating', 'bug', params), self._mh.fromhere())

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

            root = {}
            for key, value in params.items():
                root[key] = value
            root['token'] = self._token
            body = dumps(root)

            url = self._url + config['rest']
            res, body = self._client.send_request(url, method='POST', headers={'Accept': 'application/json'},
                                                  body=body, content_type='json')

        id = None
        if (res == 200):
            id = body['id']
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

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_updating', 'bug', id, params), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False

        ev = event.Event('track_before_update', id, params)
        if (self._mh.fire_event(ev) > 0):
            id = ev.argv(0)
            params = ev.argv(1)

        if (ev.will_run_default()):

            root = {}
            for key, value in params.items():
                root[key] = value
            root['token'] = self._token
            body = dumps(root)

            url = self._url + config['rest'] + '/' + str(id)
            res, body = self._client.send_request(url, method='PUT', headers={'Accept': 'application/json'},
                                                  body=body, content_type='json')

        result = False
        if (res == 200):
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_updated', id), self._mh.fromhere())
            ev = event.Event('track_after_update')
            self._mh.fire_event(ev)
            result = True
        else:
            self._mh.demsg('htk_on_error', self._mh._trn.msg(
                'track_error', res, body), self._mh.fromhere())

        return result
