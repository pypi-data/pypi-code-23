# -*- coding: utf-8 -*-
"""Client for Trac

.. module:: trackapps.trac
   :platform: Unix
   :synopsis: Client for Trac
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

"""

from hydratk.core.masterhead import MasterHead
from hydratk.core import event
from hydratk.lib.network.rpc.client import RPCClient
from sys import version_info


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
        self._client = RPCClient('XMLRPC')

        cfg = self._mh.cfg['Extensions']['TrackApps']['trac']
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
        """Method connects to Trac

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

            url = self._url
            if (self._user != None):
                if ('http://' in self._url):
                    url = 'http://{0}:{1}@{2}'.format(
                        self._user, self._passw, self._url.replace('http://', ''))
                elif ('https://' in self._url):
                    url = 'https://{0}:{1}@{2}'.format(
                        self._user, self._passw, self._url.replace('https://', ''))
                else:
                    url = '{0}:{1}@{2}'.format(
                        self._user, self._passw, self._url)

            url += '/{0}/login/xmlrpc'.format(self._project)
            res = self._client.init_proxy(url)

        result = False
        if (res and self._client.call_method('system.getAPIVersion')):
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_connected'), self._mh.fromhere())
            ev = event.Event('track_after_connect')
            self._mh.fire_event(ev)
            self._is_connected = True
            result = True

        return result

    def read(self, id=None, fields=None, query=None):
        """Method reads records

        Args: 
           id (int): record id         
           fields (list): fields to be returned, default all
           query (str): query, see Trac doc

        Returns:
           tuple: result (bool), records (list of dictionary)

        Raises:
           event: track_before_read
           event: track_after_read

        """

        message = 'id:{0}, fields:{1}, query:{2}'.format(id, fields, query)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_reading', message), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False, None

        if (fields == None and self._return_fields != None):
            fields = self._return_fields

        ev = event.Event('track_before_read', id, fields, query)
        if (self._mh.fire_event(ev) > 0):
            id = ev.argv(0)
            fields = ev.argv(1)
            query = ev.argv(2)

        if (ev.will_run_default()):

            if (id != None):
                body = self._client.call_method('ticket.get', id)
                recs = [body] if (body != None) else []
            else:
                rec_id = self._client.call_method('ticket.query', query)
                recs = []
                for id in rec_id:
                    recs.append(self._client.call_method('ticket.get', id))

            result = False
            records = None

            if (len(recs) > 0):

                records = []
                for rec in recs:
                    record = {}

                    record['id'] = rec[0]
                    for key, value in rec[3].items():
                        if (fields == None or key in fields):
                            record[key] = str(value)

                    if (record != {}):
                        records.append(record)

                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_read', len(records)), self._mh.fromhere())
                ev = event.Event('track_after_read')
                self._mh.fire_event(ev)
                result = True

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

            summary, description, attrs = None, None, {}
            for key, value in params.items():
                if (key == 'summary'):
                    summary = str(value)
                elif (key == 'description'):
                    description = str(value)
                else:
                    attrs[key] = str(value).decode('utf8') if (
                        version_info[0] == 2) else str(value)

        id = self._client.call_method(
            'ticket.create', summary, description, attrs)
        if (id != None):
            id = int(id)
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_created', id), self._mh.fromhere())
            ev = event.Event('track_after_create')
            self._mh.fire_event(ev)

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
            'track_updating', 'issue', id, params), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False

        ev = event.Event('track_before_update', id, params)
        if (self._mh.fire_event(ev) > 0):
            id = ev.argv(0)
            params = ev.argv(1)

        if (ev.will_run_default()):

            attrs = {}
            for key, value in params.items():
                attrs[key] = str(value).decode('utf8') if (
                    version_info[0] == 2) else str(value)

            body = self._client.call_method(
                'ticket.update', id, 'comment', attrs)

        result = False
        if (body != None):
            result = True
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_updated', id), self._mh.fromhere())
            ev = event.Event('track_after_update')
            self._mh.fire_event(ev)

        return result

    def delete(self, id):
        """Method deletes record

        Args: 
           id (int): record id 

        Returns:
           bool: result

        Raises:
           event: track_before_delete
           event: track_after_delete

        """

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_deleting', 'issue', id), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False

        ev = event.Event('track_before_delete', id)
        if (self._mh.fire_event(ev) > 0):
            id = ev.argv(0)

        if (ev.will_run_default()):
            body = self._client.call_method('ticket.delete', id)

        result = False
        if (body != None):
            result = True
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_deleted', id), self._mh.fromhere())
            ev = event.Event('track_after_delete')
            self._mh.fire_event(ev)

        return result
