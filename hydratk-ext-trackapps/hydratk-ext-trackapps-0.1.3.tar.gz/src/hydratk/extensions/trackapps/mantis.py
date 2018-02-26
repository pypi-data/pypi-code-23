# -*- coding: utf-8 -*-
"""Client for Mantis

.. module:: trackapps.mantis
   :platform: Unix
   :synopsis: Client for Mantis
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
from hydratk.lib.network.soap.client import SOAPClient
from lxml.etree import Element, SubElement, tostring

config = {
    'wsdl': '/api/soap/mantisconnect.php?wsdl',
    'ns': '{http://futureware.biz/mantisconnect}'
}

rec_fields = {
    'id': 'standard',
    'view_state': 'object_ref',
    'last_updated': 'date',
    'project': 'object_ref',
    'category': 'standard',
    'priority': 'object_ref',
    'severity': 'object_ref',
    'status': 'object_ref',
    'reporter': 'account_data',
    'summary': 'standard',
    'version': 'standard',
    'build': 'standard',
    'platform': 'standard',
    'os': 'standard',
    'os_build': 'standard',
    'reproducibility': 'object_ref',
    'date_submitted': 'date',
    'sponsorship_total': 'standard',
    'handler': 'account_data',
    'projection': 'object_ref',
    'eta': 'object_ref',
    'resolution': 'object_ref',
    'fixed_in_version': 'standard',
    'target_version': 'standard',
    'description': 'standard',
    'steps_to_reproduce': 'standard',
    'additional_information': 'standard',
    'attachments': 'attachment_data_array',
    'relationships': 'relationship_data_array',
    'due_date': 'date',
    'monitors': 'account_data_array',
    'sticky': 'standard',
    'tags': 'object_ref_array'
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
        self._client = SOAPClient()

        cfg = self._mh.cfg['Extensions']['TrackApps']['mantis']
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
    def project_id(self):
        """ project_id property getter """

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

    def connect(self, url=None, user=None, passw=None, project=None):
        """Method connects to Mantis

        Args:    
           url (str): URL        
           user (str): username
           passw (str): password
           project (str): QC project

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

            url = self._url + config['wsdl']
            res = self._client.load_wsdl(url)

        if (res):

            root = Element(config['ns'] + 'mc_project_get_id_from_name')
            SubElement(root, 'username').text = self._user
            SubElement(root, 'password').text = self._passw
            SubElement(root, 'project_name').text = self._project

            res = self._client.send_request(
                'mc_project_get_id_from_name', body=tostring(root))
            if (res != None and res != 0):
                self._project_id = res
                self._is_connected = True
                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_connected'), self._mh.fromhere())
                ev = event.Event('track_after_connect')
                self._mh.fire_event(ev)
            else:
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_missing_project', project), self._mh.fromhere())
                res = False

        return res

    def read(self, id=None, fields=None, page=-1, per_page=-1):
        """Method reads records

        Args: 
           id (int): record id         
           fields (list): fields to be returned, default all
           page (int): page number
           per_page (int): records per page

        Returns:
           tuple: result (bool), records (list of dictionary)

        Raises:
           event: track_before_read
           event: track_after_read

        """

        message = 'id:{0}, fields:{1}, page:{2}, per_page:{3}'.format(
            id, fields, page, per_page)
        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
            'track_reading', message), self._mh.fromhere())

        if (not self._is_connected):
            self._mh.demsg('htk_on_warning', self._mh._trn.msg(
                'track_not_connected'), self._mh.fromhere())
            return False, None

        if (fields == None and self._return_fields != None):
            fields = self._return_fields
        elif (fields == 'all'):
            fields = None

        ev = event.Event('track_before_read', id, fields, page, per_page)
        if (self._mh.fire_event(ev) > 0):
            id = ev.argv(0)
            fields = ev.argv(1)
            page = ev.argv(2)
            per_page = ev.argv(3)

        if (ev.will_run_default()):

            if (id != None):
                root = Element(config['ns'] + 'mc_issue_get')
                SubElement(root, 'username').text = self._user
                SubElement(root, 'password').text = self._passw
                SubElement(root, 'issue_id').text = str(id)
                res = self._client.send_request(
                    'mc_issue_get', body=tostring(root))
            else:
                root = Element(config['ns'] + 'mc_project_get_issues')
                SubElement(root, 'username').text = self._user
                SubElement(root, 'password').text = self._passw
                SubElement(root, 'project_id').text = str(self._project_id)
                SubElement(root, 'page_number').text = str(page)
                SubElement(root, 'per_page').text = str(per_page)
                res = self._client.send_request(
                    'mc_project_get_issues', body=tostring(root))

            result = False
            records = None
            if (res != None):
                if (id != None):
                    parsed = self._parse_record(res, fields)
                    if (parsed != {}):
                        records = parsed
                    cnt = 1
                else:
                    records = []
                    for item in res:
                        parsed = self._parse_record(item, fields)
                        if (parsed != {}):
                            records.append(parsed)
                    cnt = len(records)
                result = True

                self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                    'track_read', cnt), self._mh.fromhere())
                ev = event.Event('track_after_read')
                self._mh.fire_event(ev)

            return (result, records)

    def create(self, params):
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

            root = Element(config['ns'] + 'mc_issue_add')
            SubElement(root, 'username').text = self._user
            SubElement(root, 'password').text = self._passw
            root.append(self._toxml(params))

            res = self._client.send_request(
                'mc_issue_add', body=tostring(root))

        id = None
        if (res != None):
            id = int(res)
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

            record = self.read(id, fields='all')[1]
            if (record == None or len(record) == 0):
                self._mh.demsg('htk_on_error', self._mh._trn.msg(
                    'track_unknown_record', id), self._mh.fromhere())
                return None
            params_old = record
            for key, value in params.items():
                params_old[key] = value

            root = Element(config['ns'] + 'mc_issue_update')
            SubElement(root, 'username').text = self._user
            SubElement(root, 'password').text = self._passw
            SubElement(root, 'issueId').text = str(id)
            root.append(self._toxml(params_old))

            res = self._client.send_request(
                'mc_issue_update', body=tostring(root))

        result = False
        if (res != None):
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

            root = Element(config['ns'] + 'mc_issue_delete')
            SubElement(root, 'username').text = self._user
            SubElement(root, 'password').text = self._passw
            SubElement(root, 'issue_id').text = str(id)

            res = self._client.send_request(
                'mc_issue_delete', body=tostring(root))

        result = False
        if (res == True):
            result = True
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg(
                'track_deleted', id), self._mh.fromhere())
            ev = event.Event('track_after_delete')
            self._mh.fire_event(ev)

        return result

    def _parse_record(self, rec, fields=None):
        """Method parses record

        Args: 
           rec (xml): record in xml form
           fields (list): fields to be returned, default all 

        Returns:
           dict: parsed record

        """

        record = {}

        for key, value in rec_fields.items():
            if ((fields == None or key in fields) and hasattr(rec, key)):
                if (value == 'standard'):
                    record[key] = getattr(rec, key)
                elif (value == 'date'):
                    record[key] = str(getattr(rec, key))
                elif (value == 'object_ref'):
                    attr = getattr(rec, key)
                    id = attr.id if (hasattr(attr, 'id')) else None
                    name = attr.name if (hasattr(attr, 'name')) else None
                    record[key] = {'id': id, 'name': name}
                elif (value == 'object_ref_array'):
                    array = []
                    for item in getattr(rec, key):
                        id = item.id if (hasattr(item, 'id')) else None
                        name = item.name if (hasattr(item, 'name')) else None
                        array.append({'id': id, 'name': name})
                    record[key] = array
                elif (value == 'account_data'):
                    attr = getattr(rec, key)
                    id = attr.id if (hasattr(attr, 'id')) else None
                    name = attr.name if (hasattr(attr, 'name')) else None
                    real_name = attr.real_name if (
                        hasattr(attr, 'real_name')) else None
                    email = attr.email if (hasattr(attr, 'email')) else None
                    record[key] = {
                        'id': id, 'name': name, 'real_name': real_name, 'email': email}
                elif (value == 'account_data_array'):
                    array = []
                    for item in getattr(rec, key):
                        id = item.id if (hasattr(item, 'id')) else None
                        name = item.name if (hasattr(item, 'name')) else None
                        real_name = item.real_name if (
                            hasattr(item, 'real_name')) else None
                        email = item.email if (
                            hasattr(item, 'email')) else None
                        array.append(
                            {'id': id, 'name': name, 'real_name': real_name, 'email': email})
                elif (value == 'attachment_data_array'):
                    array = []
                    for item in getattr(rec, key):
                        id = item.id if (hasattr(item, 'id')) else None
                        filename = item.filename if (
                            hasattr(item, 'filename')) else None
                        size = item.size if (hasattr(item, 'size')) else None
                        download_url = item.download_url if (
                            hasattr(item, 'download_url')) else None
                        user_id = item.user_id if (
                            hasattr(item, 'user_id')) else None
                        array.append({'id': id, 'filename': filename, 'size': size,
                                      'content_type': item.content_type, 'date_submitted': item.date_submitted,
                                      'download_url': download_url, 'user_id': user_id})
                    record[key] = array
                elif (value == 'relationship_data_array'):
                    array = []
                    for item in getattr(rec, key):
                        id = item.id if (hasattr(item, 'id')) else None
                        type_id = item.type.id if (
                            hasattr(item, 'type') and hasattr(item.type, 'id')) else None
                        type_name = item.type.name if (
                            hasattr(item, 'type') and hasattr(item.type, 'name')) else None
                        target_id = item.target_id if (
                            hasattr(item, 'target_id')) else None
                        array.append({'id': id, 'type': {'id': type_id, 'name': type_name},
                                      'target_id': target_id})
                    record[key] = array

        return record

    def _toxml(self, params):
        """Method creates record in xml

        Args: 
           params (dict): record content, key - field name, value - field value

        Returns:
           xml: record

        """

        root = Element('issue')

        if ('project' not in params):
            elem = SubElement(root, 'project')
            SubElement(elem, 'id').text = str(self._project_id)
            SubElement(elem, 'name').text = self._project

        for key, value in params.items():
            type = rec_fields[key] if (key in rec_fields) else 'standard'

            if (type in ('standard', 'date')):
                SubElement(root, key).text = str(value)
            elif (type == 'object_ref'):
                elem = SubElement(root, key)
                SubElement(elem, 'id').text = str(
                    value['id']) if ('id' in value) else None
                SubElement(elem, 'name').text = value['name'].decode('utf8') if (
                    'name' in value and value['name'] != None) else None
            elif (type == 'object_ref_array'):
                elem = SubElement(root, key)
                for item in value:
                    el_item = Element('item')
                    SubElement(elem, 'id').text = item['id'] if (
                        'id' in item) else None
                    SubElement(elem, 'name').text = item['name'].decode('utf8') if (
                        'name' in item and item['name'] != None) else None
                    elem.append(item)
            elif (type == 'account_data'):
                elem = SubElement(root, key)
                SubElement(elem, 'id').text = str(
                    value['id']) if ('id' in value) else None
                SubElement(elem, 'name').text = value['name'].decode('utf8') if (
                    'name' in value and value['name'] != None) else None
                SubElement(elem, 'real_name').text = value['real_name'].decode('utf8') if (
                    'real_name' in value and value['real_name'] != None) else None
                SubElement(elem, 'email').text = value['email'].decode('utf8') if (
                    'email' in value and value['email'] != None) else None
            elif (type == 'account_data_array'):
                elem = SubElement(root, key)
                for item in value:
                    el_item = Element('item')
                    SubElement(elem, 'id').text = str(
                        item['id']) if ('id' in item) else None
                    SubElement(elem, 'name').text = item['name'].decode('utf8') if (
                        'name' in item and item['name'] != None) else None
                    SubElement(elem, 'real_name').text = item['real_name'].decode('utf8') if (
                        'real_name' in item and item['real_name'] != None) else None
                    SubElement(elem, 'email').text = item['email'].decode('utf8') if (
                        'email' in item and item['email'] != None) else None
                    elem.append(item)
            elif (type == 'attachment_data_array'):
                elem = SubElement(root, key)
                for item in value:
                    el_item = Element('item')
                    SubElement(elem, 'id').text = str(
                        item['id']) if ('id' in item) else None
                    SubElement(elem, 'filename').text = item['filename'].decode('utf8') if (
                        'filename' in item and item['filename'] != None) else None
                    SubElement(elem, 'size').text = item['size'] if (
                        'size' in item) else None
                    SubElement(elem, 'download_url').text = item['download_url'] if (
                        'download_url' in item) else None
                    SubElement(elem, 'user_id').text = item['user_id'] if (
                        'user_id' in item) else None
                    elem.append(item)
            elif (type == 'relationship_data_array'):
                elem = SubElement(root, key)
                for item in value:
                    el_item = Element('item')
                    SubElement(elem, 'id').text = str(
                        item['id']) if ('id' in item) else None
                    if ('type' in item):
                        el_type = SubElement(el_item)
                        SubElement(el_type, 'id').text = str(
                            item['type']['id']) if ('id' in item['type']) else None
                        SubElement(el_type, 'name').text = item['type']['name'].decode('utf8') if (
                            'name' in item['type'] and item['type']['name'] != None) else None
                    SubElement(elem, 'target_id').text = item['target_id'] if (
                        'target_id' in item) else None
                    elem.append(item)

        return root
