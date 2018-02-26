# -*- coding: utf-8 -*-
"""Extension for security testing tools

.. module:: security.security
   :platform: Unix
   :synopsis: Extension for security testing tools
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from sys import exit
from hydratk.core import extension, bootstrapper
from hydratk.lib.console.commandlinetool import CommandlineTool
import hydratk.lib.system.config as syscfg

dep_modules = {
    'hydratk': {
        'min-version': '0.5.0',
        'package': 'hydratk'
    },
    'msgpack': {
        'min-version': '0.4.8',
        'package': 'msgpack-python'
    },
    'requests': {
        'min-version': '2.11.1',
        'package': 'requests'
    },
    'simplejson': {
        'min-version': '3.8.2',
        'package': 'simplejson'
    },
    'zapv2': {
        'min-version': '0.0.10',
        'package': 'python-owasp-zap-v2.4'
    }
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

        self._ext_id = 'security'
        self._ext_name = 'Security'
        self._ext_version = '0.1.0'
        self._ext_author = 'Petr Rašek <bowman@hydratk.org>, HydraTK team <team@hydratk.org>'
        self._ext_year = '2017-2018'

        if (not self._check_dependencies()):
            exit(0)

    def _check_dependencies(self):
        """Method checks dependent modules

        Args:            
           none

        Returns:
           bool    

        """

        return bootstrapper._check_dependencies(dep_modules, 'hydratk-ext-security')

    def _uninstall(self):
        """Method returns additional uninstall data 

        Args:            
           none

        Returns:
           tuple: list (files), list (modules)  

        """

        files = [
            '/usr/share/man/man1/security.1',
            '{0}/hydratk/conf.d/hydratk-ext-security.conf'.format(syscfg.HTK_ETC_DIR)
        ]

        return files, dep_modules

    def _register_actions(self):
        """Method registers actions

        Args:
           none            

        Returns:
           void    

        """

        if (self._mh.cli_cmdopt_profile == 'security'):
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

        self._mh.match_cli_command('sec-msf')
        self._mh.match_cli_command('sec-zap')

        hook = [
            {'command': 'sec-msf', 'callback': self.sec_msf},
            {'command': 'sec-zap', 'callback': self.sec_zap}
        ]

        self._mh.register_command_hook(hook)

        self._mh.match_long_option('sec-action', True, 'sec-action')
        self._mh.match_long_option('sec-area', True, 'sec-area')
        self._mh.match_long_option('sec-format', True, 'sec-format')
        self._mh.match_long_option('sec-host', True, 'sec-host')
        self._mh.match_long_option('sec-method', True, 'sec-method')
        self._mh.match_long_option('sec-output', True, 'sec-output')
        self._mh.match_long_option('sec-params', True, 'sec-params')
        self._mh.match_long_option('sec-passw', True, 'sec-passw')
        self._mh.match_long_option('sec-path', True, 'sec-path')
        self._mh.match_long_option('sec-port', True, 'sec-port')
        self._mh.match_long_option('sec-type', True, 'sec-type')
        self._mh.match_long_option('sec-url', True, 'sec-url')
        self._mh.match_long_option('sec-user', True, 'sec-user')

    def _register_standalone_actions(self):
        """Method registers command hooks for standalone mode

        Args:  
           none        

        Returns:
           void

        """

        option_profile = 'security'
        help_title = '{h}' + self._ext_name + ' v' + self._ext_version + '{e}'
        cp_string = '{u}' + "(c) " + self._ext_year + \
            " " + self._ext_author + '{e}'
        self._mh.set_cli_appl_title(help_title, cp_string)

        self._mh.match_cli_command('msf', option_profile)
        self._mh.match_cli_command('zap', option_profile)

        hook = [
            {'command': 'msf', 'callback': self.sec_msf},
            {'command': 'zap', 'callback': self.sec_zap}
        ]
        self._mh.register_command_hook(hook)

        self._mh.match_cli_command('help', option_profile)

        self._mh.match_long_option('action', True, 'sec-action', False, option_profile)
        self._mh.match_long_option('area', True, 'sec-area', False, option_profile)
        self._mh.match_long_option('format', True, 'sec-format', False, option_profile)
        self._mh.match_long_option('host', True, 'sec-host', False, option_profile)
        self._mh.match_long_option('method', True, 'sec-method', False, option_profile)
        self._mh.match_long_option('output', True, 'sec-output', False, option_profile)
        self._mh.match_long_option('params', True, 'sec-params', False, option_profile)
        self._mh.match_long_option('passw', True, 'sec-passw', False, option_profile)
        self._mh.match_long_option('path', True, 'sec-path', False, option_profile)
        self._mh.match_long_option('port', True, 'sec-port', False, option_profile)
        self._mh.match_long_option('type', True, 'sec-type', False, option_profile)
        self._mh.match_long_option('url', True, 'sec-url', False, option_profile)
        self._mh.match_long_option('user', True, 'sec-user', False, option_profile)

        self._mh.match_cli_option(('c', 'config'), True, 'config', False, option_profile)
        self._mh.match_cli_option(('d', 'debug'), True, 'debug', False, option_profile)
        self._mh.match_cli_option(('e', 'debug-channel'), True, 'debug-channel', False, option_profile)
        self._mh.match_cli_option(('l', 'language'), True, 'language', False, option_profile)
        self._mh.match_cli_option(('m', 'run-mode'), True, 'run-mode', False, option_profile)
        self._mh.match_cli_option(('f', 'force'), False, 'force', False, option_profile)
        self._mh.match_cli_option(('i', 'interactive'), False, 'interactive', False, option_profile)
        self._mh.match_cli_option(('h', 'home'), False, 'home', False, option_profile)

    def sec_msf(self):
        """Method handles command sec-msf

        Run MSF (MetaSploit Framework) command

        Args:
           none

        Returns:
           void                 

        """

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('sec_received_cmd', 'sec-msf'), self._mh.fromhere())

        action = CommandlineTool.get_input_option('sec-action')
        if (not action):
            print('Missing option action')
        elif (action not in ['call', 'help', 'start', 'stop']):
            print('Action not in call|help|start|stop')
        else:

            rpc_path = CommandlineTool.get_input_option('sec-path')
            host = CommandlineTool.get_input_option('sec-host')
            port = CommandlineTool.get_input_option('sec-port')
            user = CommandlineTool.get_input_option('sec-user')
            passw = CommandlineTool.get_input_option('sec-passw')
            area = CommandlineTool.get_input_option('sec-area')
            method = CommandlineTool.get_input_option('sec-method')
            in_params = CommandlineTool.get_input_option('sec-params')

            host = None if (not host) else host
            port = None if (not port) else port
            user = None if (not user) else user
            passw = None if (not passw) else passw

            from hydratk.extensions.security.msf import Client
            c = Client(host, port, user, passw)

            if (action == 'start'):
                rpc_path = 'msfrpcd' if (not rpc_path) else rpc_path
                result = c.start(rpc_path)
                if (not result):
                    print('Failed to start MSF')

            elif (action == 'stop'):
                result = c.stop()
                if (not result):
                    print('Failed to stop MSF')

            elif (action == 'call'):
                if (not method):
                    print('Missing option method')
                else:
                    params = []
                    if (in_params != False):
                        for param in in_params.split('|'):
                            if (':' in param):
                                key, val = param.split(':')
                                params.append({key: val})
                            else:
                                params.append(param)
                    
                    result, out = c.call(method, params)
                    if (not result):
                        print('Failed to call MSF method {0}'.format(method))
                    else:
                        print(out)

            elif (action == 'help'):
                area = None if (not area) else area
                method = None if (not method) else method
                out = c.api_help(area, method)
                print(out)

    def sec_zap(self):
        """Method handles command sec-zap

        Run ZAP (Zed Attack Proxy) command

        Args:
           none

        Returns:
           void                 

        """

        self._mh.demsg('htk_on_debug_info', self._mh._trn.msg('sec_received_cmd', 'sec-zap'), self._mh.fromhere())

        action = CommandlineTool.get_input_option('sec-action')
        if (not action):
            print('Missing option action')
        elif (action not in ['export', 'scan', 'spider', 'start', 'stop']):
            print('Action not in export|scan|spider|start|stop')
        else:

            proxy_path = CommandlineTool.get_input_option('sec-path')
            host = CommandlineTool.get_input_option('sec-host')
            port = CommandlineTool.get_input_option('sec-port')
            url = CommandlineTool.get_input_option('sec-url')
            method = CommandlineTool.get_input_option('sec-method')
            in_params = CommandlineTool.get_input_option('sec-params')
            out_type = CommandlineTool.get_input_option('sec-type')
            out_format = CommandlineTool.get_input_option('sec-format')
            output = CommandlineTool.get_input_option('sec-output')

            host = None if (not host) else host
            port = None if (not port) else port
            url = None if (not url) else url

            from hydratk.extensions.security.zap import Client
            c = Client(host, port)

            params = None
            if (in_params != False):
                params = {}
                for param in in_params.split('|'):
                    key, val = param.split(':')
                    params[key] = val

            if (action == 'start'):
                proxy_path = 'zap.sh' if (not proxy_path) else proxy_path
                result = c.start(proxy_path)
                if (not result):
                    print('Failed to start ZAP')

            elif (action == 'stop'):
                result = c.stop()
                if (not result):
                    print('Failed to stop ZAP')

            elif (action == 'spider'):
                if (url == None):
                    print('Missing option url')
                else:
                    result, cnt = c.spider(url, params)
                    if (result):
                        print('{0} urls found'.format(cnt))
                    else:
                        print('Spider failed')

            elif (action == 'scan'):
                if (url == None):
                    print('Missing option url')
                else:
                    method = None if (not method) else method
                    result, cnt = c.scan(url, method, params)
                    if (result):
                        print ('{0} alerts found'.format(cnt))
                    else:
                        print('Scan failed')

            elif (action == 'export'):
                out_type = 'alert' if (not out_type) else out_type
                out_format = 'json' if (not out_format) else out_format
                output = None if (not output) else output

                if (out_type not in ['alert', 'msg', 'url']):
                    print('Type not in alert|msg|url')
                elif (out_format not in ['har', 'html', 'json', 'md', 'xml']):
                    print('Format not in har|html|json|md|xml')
                elif (out_type == 'alert' and out_format not in ['html', 'json', 'md', 'xml']):
                    print('Format not in html|json|md|xml for type alert')
                elif (out_type == 'msg' and out_format not in ['har', 'json']):
                    print('Format not in har|json for type msg')
                elif (out_type == 'url' and out_format not in ['json']):
                    print('Format not in json for type url')
                else:
                    result, output = c.export(out_type, out_format, output, url)
                    if (result):
                        print('File {0} generated'.format(output))
                    else:
                        print('Failed to generate export')
