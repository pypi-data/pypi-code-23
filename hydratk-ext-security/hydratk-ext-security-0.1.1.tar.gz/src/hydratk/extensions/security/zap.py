# -*- coding: utf-8 -*-
"""ZAP (Zed Attack Proxy) client

.. module:: security.zap
   :platform: Unix
   :synopsis: ZAP (Zed Attack Proxy) client
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

"""
Events:
-------
zap_before_start
zap_after_start
zap_before_stop
zap_after_stop
zap_before_spider
zap_after_spider
zap_before_scan
zap_after_scan
zap_before_export
zap_after_export

"""

from hydratk.core.masterhead import MasterHead
from hydratk.core import event
from zapv2 import ZAPv2
from os import path, devnull
from subprocess import Popen
from time import sleep
from sys import stdout, version_info
from simplejson import dumps

if (version_info[0] == 2):
    from urllib import urlencode
else:
    from urllib.parse import urlencode


class Client(object):
    """Class Client
    """

    _mh = None
    _client = None
    _path = None
    _host = None
    _port = None

    def __init__(self, host=None, port=None):
        """Class constructor

        Called when object is initialized

        Args:
            host (str): proxy host, override default configuration 127.0.0.1
            port (int): proxy port, override default configuration 8080

        """

        self._mh = MasterHead.get_head()

        cfg = self._mh.cfg['Extensions']['Security']['zap']
        self._path = cfg['path']
        self._host = cfg['host'] if (host == None) else host
        self._port = cfg['port'] if (port == None) else port

        proxy = 'http://{0}:{1}'.format(self._host, self._port)
        self._client = ZAPv2(proxies={'http': proxy, 'https:': proxy})

    @property
    def client(self):
        """ client property getter """

        return self._client

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

    def start(self, proxy_path=None):
        """Method starts proxy

        Args:
            proxy_path (str): path to proxy control script

        Returns:
            bool: result

        Raises:
            event: zap_before_start
            event: zap_after_start     

        """

        try:

            self._path = self._path if (proxy_path == None) else proxy_path
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('zap_start', self._path, self._host, self._port), self._mh.fromhere())

            ev = event.Event('zap_before_start')
            self._mh.fire_event(ev)

            if (ev.will_run_default()):
                if (path.exists(self._path)):
                    cmd = [self._path, '-daemon', '-config', 'api.disablekey=true', '-host', self._host, '-port', str(self._port)]
                    Popen(cmd, stdout=open(devnull, 'w'))
                    sleep(10)
                    self._client.core.version
                else:
                    raise ValueError('Path {0} not found'.format(self._path))

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('zap_started'), self._mh.fromhere())
            ev = event.Event('zap_after_start')
            self._mh.fire_event(ev)

            return True

        except (Exception, ValueError) as ex:
            self._mh.demsg('htk_on_error', 'error: {0}'.format(ex), self._mh.fromhere())
            return False

    def stop(self):
        """Method stops proxy

        Args:
            none

        Returns:
            bool: result

        Raises:
            event: zap_before_stop
            event: zap_after_stop     

        """

        try:
            
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('zap_stop'), self._mh.fromhere())
            ev = event.Event('zap_before_stop')
            self._mh.fire_event(ev)
            
            if (ev.will_run_default()):
                self._client.core.shutdown()
                
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('zap_stopped'), self._mh.fromhere())
            ev = event.Event('zap_after_stop')
            self._mh.fire_event(ev)

            return True                

        except Exception as ex:
            self._mh.demsg('htk_on_error', 'error: {0}'.format(ex), self._mh.fromhere())
            return False            

    def spider(self, url, params=None):
        """Method executes spider

        Args:
            url (str): URL
            params (dict): request parameters

        Returns:
            tuple: bool (result), int (count of urls)

        Raises:
            event: zap_before_spider
            event: zap_after_spider

        """

        try:

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('zap_spider_start', url, params), self._mh.fromhere())
            ev = event.Event('zap_before_spider', url, params)
            if (self._mh.fire_event(ev) > 0):
                url = ev.argv(0)
                params = ev.argv(1)
                
            if (ev.will_run_default()):
                if (params != None):
                    params = urlencode(params)
                    url += '?' + params if ('?' not in url) else '&' + params

                scanid = self._client.spider.scan(url)
                if (not scanid.isnumeric()):
                    raise Exception(scanid)

                while (True):
                    progress = self._client.spider.status(scanid)
                    stdout.write('\r' + self._mh._trn.msg('zap_progress', 'spider', progress))
                    stdout.flush()

                    if (int(progress) == 100):
                        stdout.write('\n')
                        stdout.flush()
                        break

                    sleep(1)
                
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('zap_spider_finish'), self._mh.fromhere())
            ev = event.Event('zap_after_spider')
            self._mh.fire_event(ev)

            return True, len(self._client.core.urls)

        except Exception as ex:
            self._mh.demsg('htk_on_error', 'error: {0}'.format(ex), self._mh.fromhere())
            return False, None

    def scan(self, url, method=None, params=None):
        """Method executes scan

        Args:
            url (str): URL
            method (str): HTTP method, default GET
            params (dict): request parameters

        Returns:
            tuple: bool (result), int (count of alerts)

        Raises:
            event: zap_before_scan
            event: zap_after_scan

        """

        try:

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('zap_scan_start', url, method, params), self._mh.fromhere())
            ev = event.Event('zap_before_scan', url, method, params)
            if (self._mh.fire_event(ev) > 0):
                url = ev.argv(0)
                method = ev.argv(1)
                params = ev.argv(2)

            if (ev.will_run_default()):
                if (method in [None, 'GET']):
                    if (params != None):
                        params = urlencode(params)
                        new_url = url + '?' + params if ('?' not in url) else url + '&' + params
                        scanid = self._client.ascan.scan(new_url)
                    else:
                        scanid = self._client.ascan.scan(url)
                else:
                    params = '' if (params == None) else urlencode(params)
                    scanid = self._client.ascan.scan(url, method=method, postdata=params)

                if (not scanid.isnumeric()):
                    raise Exception(scanid)

                while (True):
                    progress = self._client.ascan.status(scanid)
                    stdout.write('\r' + self._mh._trn.msg('zap_progress', 'scan', progress))
                    stdout.flush()

                    if (int(progress) == 100):
                        stdout.write('\n')
                        stdout.flush()
                        break

                    sleep(1)

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('zap_scan_finish'), self._mh.fromhere())
            ev = event.Event('zap_after_scan')
            self._mh.fire_event(ev)

            cnt = self._client.core.number_of_alerts(url) if (version_info[0] == 2) else int(float(self._client.core.number_of_alerts(url)))
            return True, cnt

        except Exception as ex:
            self._mh.demsg('htk_on_error', 'error: {0}'.format(ex), self._mh.fromhere())
            return False, None

    def export(self, out_type='alert', out_format='json', output=None, url=None):
        """Method executes export

        Args:
            out_type (str): output type, alert|msg|url
            out_format (str): output format, html|json|md|xml for alert, har|json for msg, json for url
            output (str): output filename
            url (str): URL for filtering

        Returns:
            tuple: bool (result), str (output filename)

        Raises:
            event: zap_before_export
            event: zap_after_export

        """

        try:
            
            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('zap_export_start', out_type, out_format, output, url), self._mh.fromhere())
            ev = event.Event('zap_before_export', out_type, out_format, output, url)
            if (self._mh.fire_event(ev) > 0):
                out_type = ev.argv(0)
                out_format = ev.argv(1)
                output = ev.argv(2)
                url = ev.argv(3)

            if (ev.will_run_default()):
                if (out_type not in ['alert', 'msg', 'url']):
                    raise ValueError('Invalid type {0}'.format(out_type))
                elif (out_format not in ['har', 'html', 'json', 'md', 'xml']):
                    raise ValueError('Invalid format {0}'.format(out_format))
                elif ((out_type == 'alert' and out_format not in ['html', 'json', 'md', 'xml']) or
                      (out_type == 'msg' and out_format not in ['har', 'json']) or (out_type == 'url' and out_format != 'json')):
                    raise ValueError('Invalid format {0} for type {1}'.format(out_format, out_type))

                if (out_type == 'url'):
                    data = dumps(self._client.core.urls, indent=1)
                elif (out_type == 'msg'):
                    data = dumps(self._client.core.messages(url), indent=4) if (out_format == 'json') else self._client.core.messages_har(url)
                elif (out_type == 'alert'):
                    if (out_format == 'json'):
                        data = dumps(self._client.core.alerts(url), indent=4)
                    elif (out_format == 'html'):
                        data = self._client.core.htmlreport()
                    elif (out_format == 'md'):
                        data = self._client.core.mdreport()
                    elif (out_format == 'xml'):
                        data = self._client.core.xmlreport()

                output = output if (output != None) else '{0}.{1}'.format(out_type, out_format)
                with open(output, 'w') as f:
                    f.write(data)

            self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('zap_export_finish'), self._mh.fromhere())
            ev = event.Event('zap_after_export')
            self._mh.fire_event(ev)
            
            return True, output

        except (Exception, ValueError) as ex:
            self._mh.demsg('htk_on_error', 'error: {0}'.format(ex), self._mh.fromhere())
            return False, None
