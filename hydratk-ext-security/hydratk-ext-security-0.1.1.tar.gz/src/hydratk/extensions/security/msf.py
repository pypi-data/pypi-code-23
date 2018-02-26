# -*- coding: utf-8 -*-
"""MSF (MetaSploit Framework) client

.. module:: security.msf
   :platform: Unix
   :synopsis: MSF (MetaSploit Framework) client
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

"""
Events:
-------
msf_before_start
msf_after_start
msf_before_stop
msf_after_stop
msf_before_call
msf_after_call

"""

from hydratk.extensions.security.msf_api import api
from hydratk.core.masterhead import MasterHead
from hydratk.core import event
from msgpack import packb, unpackb
from requests import post
from requests.exceptions import RequestException
from requests.packages.urllib3 import disable_warnings
from os import path, devnull
from subprocess import Popen
from psutil import process_iter
from time import sleep
from sys import version_info


class Client(object):
    """Class Client
    """

    _mh = None
    _path = None
    _host = None
    _port = None
    _user = None
    _passw = None
    _token = None

    def __init__(self, host=None, port=None, user=None, passw=None):
        """Class constructor

        Called when object is initialized

        Args:
            host (str): host, override default configuration 127.0.0.1
            port (int): port, override default configuration 55553
            user (str): username, override default configuration msf
            passw (str): password, override default configuration msf

        """

        self._mh = MasterHead.get_head()

        cfg = self._mh.cfg['Extensions']['Security']['msf']
        self._path = cfg['path']
        self._host = cfg['host'] if (host == None) else host
        self._port = cfg['port'] if (port == None) else port
        self._user = cfg['user'] if (user == None) else user
        self._passw = cfg['passw'] if (passw == None) else passw

        disable_warnings()

    @property
    def path(self):
        """ path property getter """

        return self._path

    @property
    def host(self):
        """ host property getter """

        return self._host

    @property
    def port(self):
        """ port property getter """

        return self._port

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

    def start(self, rpc_path=None):
        """Method starts MSF RPC

        Args:
            rpc_path (str): path to rpc control script

        Returns:
            bool: result

        Raises:
            event: msf_before_start
            event: msf_after_start

        """

        try:

            self._path = self._path if (rpc_path == None) else rpc_path
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('msf_start', self._path, self._host, self._port,
                          self._user, self._passw), self._mh.fromhere())

            ev = event.Event('msf_before_start')
            self._mh.fire_event(ev)

            if (ev.will_run_default()):
                if (path.exists(self._path)):
                    cmd = [self._path, '-a', self._host, '-p', str(self._port), '-U', self._user, '-P', self._passw]
                    Popen(cmd, stdout=open(devnull, 'w'))
                    sleep(10)
                    if (self._get_process() == None):
                        raise Exception('Process not started')
                else:
                    raise ValueError('Path {0} not found'.format(self._path))

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('msf_started'), self._mh.fromhere())
            ev = event.Event('msf_after_start')
            self._mh.fire_event(ev)

            return True

        except (Exception, ValueError) as ex:
            self._mh.demsg('htk_on_error', 'error: {0}'.format(ex), self._mh.fromhere())
            return False

    def stop(self):
        """Method stops RPC

        Args:
            none

        Returns:
            bool: result

        Raises:
            event: msf_before_stop
            event: msf_after_stop

        """

        try:

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('msf_stop'), self._mh.fromhere())
            ev = event.Event('msf_before_stop')
            self._mh.fire_event(ev)

            if (ev.will_run_default()):
                proc = self._get_process()
                if (proc == None):
                    raise Exception('Process not started')
                proc.terminate()

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('msf_stopped'), self._mh.fromhere())
            ev = event.Event('msf_after_stop')
            self._mh.fire_event(ev)

            return True

        except Exception as ex:
            self._mh.demsg('htk_on_error', 'error: {0}'.format(ex), self._mh.fromhere())
            return False

    def call(self, method, params=[]):
        """Method calls RPC method

        Args:
            method (str): method title
            params (list): method parameters, values or dict

        Returns:
            tuple: bool (result), dict (output)

        Raises:
            event: msf_before_call
            event: msf_after_call

        """

        try:

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('msf_call_req', method, params), self._mh.fromhere())
            ev = event.Event('msf_before_call', method, params)
            if (self._mh.fire_event(ev) > 0):
                method = ev.argv(0)
                params = ev.argv(1)

            res = None
            if (ev.will_run_default()):
                url = 'https://{0}:{1}/api/'.format(self._host, self._port)
                headers = {'Content-Type': 'binary/message-pack'}

                if (method == 'auth.login' or self._token == None):
                    data = packb([method] + params) if (method == 'auth.login') else packb(['auth.login', self._user, self._passw])
                    res = post(url, data=data, headers=headers, verify=False)
                    if (res.status_code == 200):
                        res = unpackb(res.content)
                        if ('error' not in res and b'error' not in res):
                            self._token = res['token'] if (version_info[0] == 2) else res[b'token']
                        else:
                            raise Exception(res['error_message'] if (version_info[0] == 2) else res[b'error_message'])
                    else:
                        raise Exception('Failed to connect')

                if (method != 'auth.login'):
                    data = packb([method, self._token] + params)
                    res = post(url, data=data, headers=headers, verify=False)
                    if (res.status_code == 200):
                        res = unpackb(res.content)
                        if ('error' in res or b'error' in res):
                            raise Exception(res['error_message'] if (version_info[0] == 2) else res[b'error_message'])
                    else:
                        raise Exception(res.content)

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('msf_call_res', res), self._mh.fromhere())
            ev = event.Event('msf_after_call')
            self._mh.fire_event(ev)

            return True, res

        except (RequestException, Exception) as ex:
            self._mh.demsg('htk_on_error', 'error: {0}'.format(ex), self._mh.fromhere())
            return False, res

    def api_help(self, area=None, method=None):
        """Method provides RPC API help

        method != None - help for given method
        area != None - list of area methods
        area = None - list of areas

        Args:
            area (str): RPC area
            method (str): RPC method (format area.method)

        Returns:
            str: help

        """

        txt = ''
        if (method != None):
            method_s = method.split('.')
            if (len(method_s) != 2):
                txt = 'Invalid method: {0}, mandatory format area.method'.format(method)
            else:
                area, method = method_s
                if (area not in api):
                    txt = 'Unknown area: {0}'.format(area)
                elif (method not in api[area]):
                    txt = 'Unknown method: {0}.{1}'.format(area, method)
                else:
                    cfg = api[area][method]
                    txt = 'Method {0}.{1}\n  description: {2}\n  params:'.format(area, method, cfg['desc'])
                    for p in cfg['params']:
                        txt += '\n    {0} - direction: {1}, type: {2}, description: {3}'.format(p['name'], p['direction'], p['type'], p['desc'])
        elif (area != None):
            if (area not in api):
                txt = 'Unknown area: {0}'.format(area)
            else:
                txt = '{0} area methods:'.format(area)
                for key in sorted(api[area].keys()):
                    txt += '\n  {0}'.format(key)
        else:
            txt = 'Areas:'
            for key in sorted(api.keys()):
                txt += '\n  {0}'.format(key)

        return txt

    def _get_process(self):
        """Method gets RPC process

        Args:
            none

        Returns:
            obj: process

        """

        for p in process_iter():
            cmd = p.cmdline()
            if (cmd != None and len(cmd) > 0 and self._path.split('/')[-1] in cmd[0]):
                return p

        return None
