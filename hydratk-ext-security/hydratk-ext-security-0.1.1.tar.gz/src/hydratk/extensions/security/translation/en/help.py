# -*- coding: utf-8 -*-

"""This code is a part of Hydra Toolkit

.. module:: hydratk.extensions.security.translation.en.help
   :platform: Unix
   :synopsis: English language translation for Security extension help generator
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""
language = {
    'name': 'English',
    'ISO-639-1': 'en'
}

''' Security Commands '''
help_cmd = {
    'sec-msf': 'run MSF (MetaSploit Framework) command',
    'sec-zap': 'run ZAP (Zed Attack Proxy) command',

    # standalone with option profile security
    'msf': 'run MSF (MetaSploit Framework) command',
    'zap': 'run ZAP (Zed Attack Proxy) command'
}

''' Security Options '''
help_opt = {
    'sec-action': {'{h}--sec-action <string>{e}': {'description': 'action - call|start|stop', 'commands': ('sec-msf')},
                   '{h}--sec-action <string>{e}{e}': {'description': 'action - export|scan|spider|start|stop', 'commands': ('sec-zap')}},
    'sec-area': {'{h}[--sec-area <string>]{e}': {'description': 'RPC area, supported for action help', 'commands': ('sec-msf')}},
    'sec-format': {'{h}[--sec-format <string>]{e}': {'description': 'output format - har|html|json|md|xml, default json, supported for action export', 'commands': ('sec-zap')}},
    'sec-host': {'{h}[--sec-host <string>]{e}': {'description': 'host, default 127.0.0.1', 'commands': ('sec-msf', 'sec-zap')}},
    'sec-method': {'{h}[--sec-method <string>]{e}': {'description': 'RPC method name, format area.method, supported for actions call|help', 'commands': ('sec-msf')},
                   '{h}[--sec-method <string>]{e}{e}': {'description': 'HTTP method, default GET, supported for action scan', 'commands': ('sec-zap')}},
    'sec-output': {'{h}[--sec-output <filename>]{e}': {'description': 'output filename, supported for action export', 'commands': ('sec-zap')}},
    'sec-params': {'{h}[--sec-params <list>]{e}': {'description': 'method parameters val1|val2|key3:val3, supported for action call', 'commands': ('sec-msf')},
                   '{h}[--sec-params <dict>]{e}{e}': {'description': 'request parameters key1:val1|key2:val2, supported for actions scan|spider', 'commands': ('sec-zap')}},
    'sec-passw': {'{h}[--sec-passw <string>]{e}': {'description': 'password, default msf', 'commands': ('sec-msf')}},
    'sec-path': {'{h}[--sec-path <path>]{e}': {'description': 'path to daemon script, default msfrpcd, supported for action start', 'commands': ('sec-msf')},
                 '{h}[--sec-path <path>]{e}{e}': {'description': 'path to proxy control script, default zap.sh, supported for action start', 'commands': ('sec-zap')}},
    'sec-port': {'{h}[--sec-port <number>]{e}': {'description': 'RPC port, default 55553', 'commands': ('sec-msf')},
                 '{h}[--sec-port <number>]{e}{e}': {'description': 'proxy port, default 8080', 'commands': ('sec-zap')}},
    'sec-type': {'{h}[--sec-type <string>]{e}': {'description': 'output type - alert|msg|url, default alert, supported for action export', 'commands': ('sec-zap')}},
    'sec-url': {'{h}[--sec-url <string>]{e}': {'description': 'URL, supported for actions export|scan|spider', 'commands': ('sec-zap')}},
    'sec-user': {'{h}[--sec-user <string>]{e}': {'description': 'username, default msf', 'commands': ('sec-msf')}},

    # standalone with option profile security
    'action': {'{h}--action <string>{e}': {'description': 'action - call|start|stop', 'commands': ('msf')},
               '{h}--action <string>{e}{e}': {'description': 'action - export|scan|spider|start|stop', 'commands': ('zap')}},
    'area': {'{h}[--area <string>]{e}': {'description': 'RPC area, supported for action help', 'commands': ('msf')}},
    'format': {'{h}[--format <string>]{e}': {'description': 'output format - har|html|json|md|xml, default json, supported for action export', 'commands': ('zap')}},
    'host': {'{h}[--host <string>]{e}': {'description': 'host, default 127.0.0.1', 'commands': ('msf', 'zap')}},
    'method': {'{h}[--method <string>]{e}': {'description': 'RPC method name, format area.method, supported for actions call|help', 'commands': ('msf')},
               '{h}[--method <string>]{e}{e}': {'description': 'HTTP method, default GET, supported for action scan', 'commands': ('zap')}},
    'output': {'{h}[--output <filename>]{e}': {'description': 'output filename, supported for action export', 'commands': ('zap')}},
    'params': {'{h}[--params <list>]{e}': {'description': 'method parameters val1|val2|key3:val3, supported for action call', 'commands': ('msf')},
               '{h}[--params <dict>]{e}{e}': {'description': 'request parameters key1:val1|key2:val2, supported for actions scan|spider', 'commands': ('zap')}},
    'passw': {'{h}[--passw <string>]{e}': {'description': 'password, default msf', 'commands': ('msf')}},
    'path': {'{h}[--path <path>]{e}': {'description': 'path to daemon script, default msfrpcd, supported for action start', 'commands': ('msf')},
             '{h}[--path <path>]{e}{e}': {'description': 'path to proxy control script, default zap.sh, supported for action start', 'commands': ('zap')}},
    'port': {'{h}[--port <number>]{e}': {'description': 'RPC port, default 55553', 'commands': ('msf')},
             '{h}[--port <number>]{e}{e}': {'description': 'proxy port, default 8080', 'commands': ('zap')}},
    'type': {'{h}[--type <string>]{e}': {'description': 'output type - alert|msg|url, default alert, supported for action export', 'commands': ('zap')}},
    'url': {'{h}[--url <string>]{e}': {'description': 'URL, supported for actions export|scan|spider', 'commands': ('zap')}},
    'user': {'{h}[--user <string>]{e}': {'description': 'username, default msf', 'commands': ('msf')}}
}
