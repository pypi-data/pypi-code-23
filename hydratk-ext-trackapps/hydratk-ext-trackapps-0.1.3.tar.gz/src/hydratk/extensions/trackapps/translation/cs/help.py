# -*- coding: utf-8 -*-

"""This code is a part of Hydra Toolkit

.. module:: hydratk.extensions.trackapps.translation.cs.help
   :platform: Unix
   :synopsis: Czech language translation for TrackAPps extension help generator
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""
language = {
    'name': 'Čeština',
    'ISO-639-1': 'cs'
}

''' TrackApps Commands '''
help_cmd = {
    'track': 'spustit konzolové rozšíření trackapps',

    # standalone with option profile trackapps
    'run': 'spustit konzolové rozšíření trackapps'
}

''' TrackApps Options '''
help_opt = {
    'tr-app': {'{h}--tr-app qc|bugzilla|mantis|trac|testlink{e}': {'description': 'aplikace', 'commands': ('track')}},
    'tr-action': {'{h}--tr-action read|create|update|delete{e}': {'description': 'akce, delete podporováno pro aplikace: qc|mantis|trac', 'commands': ('track')}},
    'tr-type': {'[{h}--tr-type defect|test-folder|test|test-set-folder|test-set|test-instance|test-suite|test-plan|build{e}]': {'description': 'typ entity, default defect, podporováno pro akce: read|create|update|delete, aplikace: qc|testlink', 'commands': ('track')}},
    'tr-input': {'[{h}--tr-input <soubor>{e}]': {'description': 'jméno souboru, obsah se zapíše do description tiketu, podporováno pro akce: create|update', 'commands': ('track')}},
    'tr-output': {'[{h}--tr-output <soubor>{e}]': {'description': 'jméno souboru, zápis výstupu akce, podporováno pro akci: read', 'commands': ('track')}},
    'tr-url': {'[{h}--tr-url <url>{e}]': {'description': 'url, konfigurovatelné', 'commands': ('track')}},
    'tr-user': {'[{h}--tr-user <uživatel>{e}]': {'description': 'uživatelské jméno, konfigurovatelné', 'commands': ('track')}},
    'tr-passw': {'[{h}--tr-passw <heslo>{e}]': {'description': 'heslo, konfigurovatelné', 'commands': ('track')}},
    'tr-dev-key': {'[{h}--tr-dev-key <klíč>{e}]': {'description': 'klíč vývojáře, konfigurovatelné, podporováno pro aplikaci: testlink', 'commands': ('track')}},
    'tr-domain': {'[{h}--tr-domain <doména>{e}]': {'description': 'doména, konfigurovatelné, podporováno pro aplikaci: qc', 'commands': ('track')}},
    'tr-project': {'[{h}--tr-project <projekt>{e}]': {'description': 'projekt, konfigurovatelné, podporováno pro aplikace: qc|mantis|trac|jira|testlink', 'commands': ('track')}},
    'tr-id': {'[{h}--tr-id <číslo>{e}]': {'description': 'id záznamu, podporováno pro akce: read|update|delete', 'commands': ('track')}},
    'tr-fields': {'[{h}--tr-fields <seznam>{e}]': {'description': 'požadovaná pole, jméno1,jméno2,... , podporováno pro akci: read', 'commands': ('track')}},
    'tr-query': {'[{h}--tr-query <výraz>{e}]': {'description': 'dotaz, podporováno pro akci: read, aplikace: qc|bugzilla|trac|jira', 'commands': ('track')}},
    'tr-order-by': {'[{h}--tr-order-by <výraz>{e}]': {'description': 'řazení záznamů, jméno1:směr,jméno2:směr,... , směr asc|desc, podporováno pro akci: read, aplikaci: qc', 'commands': ('track')}},
    'tr-limit': {'[{h}--tr-limit <číslo>{e}]': {'description': 'limit, podporováno pro akci: read, aplikace: qz|bugzilla|jira', 'commands': ('track')}},
    'tr-offset': {'[{h}--tr-offset <číslo>{e}]': {'description': 'offset, podporováno pro akci: read, aplikace: qc|bugzilla|jira', 'commands': ('track')}},
    'tr-page': {'[{h}--tr-page <číslo>{e}]': {'description': 'stránka záznamů, podporováno pro akci: read, aplikaci: mantis', 'commands': ('track')}},
    'tr-per-page': {'[{h}--tr-per-page <číslo>{e}]': {'description': 'počet záznamů na stránku, podporováno pro akci read: aplikaci: mantis', 'commands': ('track')}},
    'tr-params': {'[{h}--tr-params <slovník>{e}]': {'description': 'parametry záznamu, jméno1:hodnota,jméno2:hodnota, podporováno pro akce: create|update', 'commands': ('track')}},
    'tr-path': {'[{h}--tr-path <cesta>{e}]': {'description': 'adresářová cesta, dir1/dir2/... , podporováno pro případy: read/create folder|read/create test set|create test|read/create suite, aplikace: qc|testlink', 'commands': ('track')}},
    'tr-steps': {'[{h}--tr-steps <seznam>{e}]': {'description': 'kroky testu oddělené |, parametry kroku používají tvar slovníku, jméno1:hodnota,jméno2:hodnota,...|jméno1:hodnota,jméno2:hodnota,... , podporováno akci: create, aplikaci: testlink', 'commands': ('track')}},

    # standalone with option profile trackapps
    'app': {'{h}--app qc|bugzilla|mantis|trac|testlink{e}': {'description': 'aplikace', 'commands': ('run')}},
    'action': {'{h}--action read|create|update|delete{e}': {'description': 'akce, delete podporováno pro aplikace: qc|mantis|trac', 'commands': ('run')}},
    'type': {'[{h}--type defect|test-folder|test|test-set-folder|test-set|test-instance|test-suite|test-plan|build{e}]': {'description': 'typ entity, default defect, podporováno pro akce: read|create|update|delete, aplikace: qc|testlink', 'commands': ('run')}},
    'input': {'[{h}--input <soubor>{e}]': {'description': 'jméno souboru, obsah se zapíše do description tiketu, podporováno pro akce: create|update', 'commands': ('run')}},
    'output': {'[{h}--output <soubor>{e}]': {'description': 'jméno souboru, zápis výstupu akce, podporováno pro akci: read', 'commands': ('run')}},
    'url': {'[{h}--url <url>{e}]': {'description': 'url, konfigurovatelné', 'commands': ('run')}},
    'user': {'[{h}--user <uživatel>{e}]': {'description': 'uživatelské jméno, konfigurovatelné', 'commands': ('run')}},
    'passw': {'[{h}--passw <heslo>{e}]': {'description': 'heslo, konfigurovatelné', 'commands': ('run')}},
    'dev-key': {'[{h}--dev-key <klíč>{e}]': {'description': 'klíč vývojáře, konfigurovatelné, podporováno pro aplikaci: testlink', 'commands': ('run')}},
    'domain': {'[{h}--domain <doména>{e}]': {'description': 'doména, konfigurovatelné, podporováno pro aplikaci: qc', 'commands': ('run')}},
    'project': {'[{h}--project <projekt>{e}]': {'description': 'projekt, konfigurovatelné, podporováno pro aplikace: qc|mantis|trac|jira|testlink', 'commands': ('run')}},
    'id': {'[{h}--id <číslo>{e}]': {'description': 'id záznamu, podporováno pro akce: read|update|delete', 'commands': ('run')}},
    'fields': {'[{h}--fields <seznam>{e}]': {'description': 'požadovaná pole, jméno1,jméno2,... , podporováno pro akci: read', 'commands': ('run')}},
    'query': {'[{h}--query <výraz>{e}]': {'description': 'dotaz, podporováno pro akci: read, aplikace: qc|bugzilla|trac|jira', 'commands': ('run')}},
    'order-by': {'[{h}--order-by <výraz>{e}]': {'description': 'řazení záznamů, jméno1:směr,jméno2:směr,... , směr asc|desc, podporováno pro akci: read, aplikaci: qc', 'commands': ('run')}},
    'limit': {'[{h}--limit <číslo>{e}]': {'description': 'limit, podporováno pro akci: read, aplikace: qz|bugzilla|jira', 'commands': ('run')}},
    'offset': {'[{h}--offset <číslo>{e}]': {'description': 'offset, podporováno pro akci: read, aplikace: qc|bugzilla|jira', 'commands': ('run')}},
    'page': {'[{h}--page <číslo>{e}]': {'description': 'stránka záznamů, podporováno pro akci: read, aplikaci: mantis', 'commands': ('run')}},
    'per-page': {'[{h}--per-page <číslo>{e}]': {'description': 'počet záznamů na stránku, podporováno pro akci read: aplikaci: mantis', 'commands': ('run')}},
    'params': {'[{h}--params <slovník>{e}]': {'description': 'parametry záznamu, jméno1:hodnota,jméno2:hodnota, podporováno pro akce: create|update', 'commands': ('run')}},
    'path': {'[{h}--path <cesta>{e}]': {'description': 'adresářová cesta, dir1/dir2/... , podporováno pro případy: read/create folder|read/create test set|create test|read/create suite, aplikace: qc|testlink', 'commands': ('run')}},
    'steps': {'[{h}--steps <seznam>{e}]': {'description': 'kroky testu oddělené |, parametry kroku používají tvar slovníku, jméno1:hodnota,jméno2:hodnota,...|jméno1:hodnota,jméno2:hodnota,... , podporováno akci: create, aplikaci: testlink', 'commands': ('run')}}
}
