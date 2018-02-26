# -*- coding: utf-8 -*-

"""This code is a part of Hydra Toolkit

.. module:: hydratk.extensions.security.translation.cs.help
   :platform: Unix
   :synopsis: Czech language translation for Security extension help generator
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""
language = {
    'name': 'Čeština',
    'ISO-639-1': 'cs'
}

''' Security Commands '''
help_cmd = {
    'sec-msf': 'spustit příkaz pro MSF (MetaSploit Framework)',
    'sec-zap': 'spustit příkaz pro ZAP (Zed Attack Proxy)',

    # standalone with option profile security
    'msf': 'spustit příkaz pro MSF (MetaSploit Framework)',
    'zap': 'spustit příkaz pro ZAP (Zed Attack Proxy)'
}

''' Security Options '''
help_opt = {
    'sec-action': {'{h}--sec-action <string>{e}': {'description': 'akce - call|start|stop', 'commands': ('sec-msf')},
                   '{h}--sec-action <string>{e}{e}': {'description': 'akce - export|scan|spider|start|stop', 'commands': ('sec-zap')}},
    'sec-area': {'{h}[--sec-area <string>]{e}': {'description': 'RPC oblast, podporováno pro akci help', 'commands': ('sec-msf')}},
    'sec-format': {'{h}[--sec-format <string>]{e}': {'description': 'formát výstupu - har|html|json|md|xml, default json, podporováno pro akci export', 'commands': ('sec-zap')}},
    'sec-host': {'{h}[--sec-host <string>]{e}': {'description': 'host, default 127.0.0.1', 'commands': ('sec-msf', 'sec-zap')}},
    'sec-method': {'{h}[--sec-method <string>]{e}': {'description': 'RPC metoda, formát area.method, podporováno pro akce call|help', 'commands': ('sec-msf')},
                   '{h}[--sec-method <string>]{e}{e}': {'description': 'HTTP metoda, default GET, podporováno pro akci scan', 'commands': ('sec-zap')}},
    'sec-output': {'{h}[--sec-output <filename>]{e}': {'description': 'název výstupního souboru, podporováno pro akci export', 'commands': ('sec-zap')}},
    'sec-params': {'{h}[--sec-params <list>]{e}': {'description': 'parametry metody val1|val2|key3:val3, podporováno pro akci call', 'commands': ('sec-msf')},
                   '{h}[--sec-params <dict>]{e}{e}': {'description': 'parametry requestu key1:val1|key2:val2, podporováno pro akce scan|spider', 'commands': ('sec-zap')}},
    'sec-passw': {'{h}[--sec-passw <string>]{e}': {'description': 'heslo, default msf, ', 'commands': ('sec-msf')}},
    'sec-path': {'{h}[--sec-path <path>]{e}': {'description': 'cesta k daemon skriptu, default msfrpcd, podporováno pro akci start', 'commands': ('sec-msf')},
                 '{h}[--sec-path <path>]{e}{e}': {'description': 'cesta k řídícímu skriptu proxy, default zap.sh, podporováno pro akci start', 'commands': ('sec-zap')}},
    'sec-port': {'{h}[--sec-port <number>]{e}': {'description': 'RPC port, default 55553', 'commands': ('sec-msf')},
                 '{h}[--sec-port <number>]{e}{e}': {'description': 'proxy port, default 8080', 'commands': ('sec-zap')}},
    'sec-type': {'{h}[--sec-type <string>]{e}': {'description': 'typ výstupu - alert|msg|url, default alert, podporováno pro akci export', 'commands': ('sec-zap')}},
    'sec-url': {'{h}[--sec-url <string>]{e}': {'description': 'URL, podporováno pro akce export|scan|spider', 'commands': ('sec-zap')}},
    'sec-user': {'{h}[--sec-user <string>]{e}': {'description': 'user, default msf', 'commands': ('sec-msf')}},

    # standalone with option profile security
    'action': {'{h}--action <string>{e}': {'description': 'akce - call|start|stop', 'commands': ('msf')},
               '{h}--action <string>{e}{e}': {'description': 'akce - export|scan|spider|start|stop', 'commands': ('zap')}},
    'area': {'{h}[--area <string>]{e}': {'description': 'RPC oblast, podporováno pro akci help', 'commands': ('msf')}},
    'format': {'{h}[--format <string>]{e}': {'description': 'formát výstupu - har|html|json|md|xml, default json, podporováno pro akci export', 'commands': ('zap')}},
    'host': {'{h}[--host <string>]{e}': {'description': 'host, default 127.0.0.1', 'commands': ('msf', 'zap')}},
    'method': {'{h}[--method <string>]{e}': {'description': 'RPC metoda, formát area.method, podporováno pro akce call|help', 'commands': ('msf')},
               '{h}[--method <string>]{e}{e}': {'description': 'HTTP metoda, default GET, podporováno pro akci scan', 'commands': ('zap')}},
    'output': {'{h}[--output <filename>]{e}': {'description': 'název výstupního souboru, podporováno pro akci export', 'commands': ('zap')}},
    'params': {'{h}[--params <list>]{e}': {'description': 'parametry metody val1|val2|key3:val3, podporováno pro akci call', 'commands': ('msf')},
               '{h}[--params <dict>]{e}{e}': {'description': 'parametry requestu key1:val1|key2:val2, podporováno pro akce scan|spider', 'commands': ('zap')}},
    'passw': {'{h}[--passw <string>]{e}': {'description': 'heslo, default msf, ', 'commands': ('msf')}},
    'path': {'{h}[--path <path>]{e}': {'description': 'cesta k daemon skriptu, default msfrpcd, podporováno pro akci start', 'commands': ('msf')},
             '{h}[--path <path>]{e}{e}': {'description': 'cesta k řídícímu skriptu proxy, default zap.sh, podporováno pro akci start', 'commands': ('zap')}},
    'port': {'{h}[--port <number>]{e}': {'description': 'RPC port, default 55553', 'commands': ('msf')},
             '{h}[--port <number>]{e}{e}': {'description': 'proxy port, default 8080', 'commands': ('zap')}},
    'type': {'{h}[--type <string>]{e}': {'description': 'typ výstupu - alert|msg|url, default alert, podporováno pro akci export', 'commands': ('zap')}},
    'url': {'{h}[--url <string>]{e}': {'description': 'URL, podporováno pro akce export|scan|spider', 'commands': ('zap')}},
    'user': {'{h}[--user <string>]{e}': {'description': 'user, default msf', 'commands': ('msf')}},
}
