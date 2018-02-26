# -*- coding: utf-8 -*-

"""This code is a part of Hydra Toolkit

.. module:: hydratk.extensions.trackapps.translation.en.help
   :platform: Unix
   :synopsis: English language translation for TrackApps extension help generator
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""
language = {
    'name': 'English',
    'ISO-639-1': 'en'
}

''' TrackApps Commands '''
help_cmd = {
    'track': 'run trackapps command line extension',

    # standalone with option profile trackapps
    'run': 'run trackapps command line extension'
}

''' TrackApps Options '''
help_opt = {
    'tr-app': {'{h}--tr-app qc|bugzilla|mantis|trac|testlink{e}': {'description': 'application', 'commands': ('track')}},
    'tr-action': {'{h}--tr-action read|create|update|delete{e}': {'description': 'action, delete supported for apps: qc|mantis|trac', 'commands': ('track')}},
    'tr-type': {'[{h}--tr-type defect|test-folder|test|test-set-folder|test-set|test-instance|test-suite|test-plan|build{e}]': {'description': 'entity type, default defect, supported for actions: read|create|update|delete, apps: qc|testlink', 'commands': ('track')}},
    'tr-input': {'[{h}--tr-input <filename>{e}]': {'description': 'filename, content is written to ticket description, supported for actions: create|update', 'commands': ('track')}},
    'tr-output': {'[{h}--tr-output <filename>{e}]': {'description': 'filename, writes action output, supported for action: read', 'commands': ('track')}},
    'tr-url': {'[{h}--tr-url <url>{e}]': {'description': 'url, configurable', 'commands': ('track')}},
    'tr-user': {'[{h}--tr-user <username>{e}]': {'description': 'username, configurable', 'commands': ('track')}},
    'tr-passw': {'[{h}--tr-passw <password>{e}]': {'description': 'password, configurable', 'commands': ('track')}},
    'tr-dev-key': {'[{h}--tr-dev-key <key>{e}]': {'description': 'developer key, configurable, supported for app: testlink', 'commands': ('track')}},
    'tr-domain': {'[{h}--tr-domain <domain>{e}]': {'description': 'domain, configurable, supported for app: qc', 'commands': ('track')}},
    'tr-project': {'[{h}--tr-project <project>{e}]': {'description': 'project, configurable, supported for apps: qc|mantis|trac|jira|testlink', 'commands': ('track')}},
    'tr-id': {'[{h}--tr-id <num>{e}]': {'description': 'record id, supported for actions: read|update|delete', 'commands': ('track')}},
    'tr-fields': {'[{h}--tr-fields <list>{e}]': {'description': 'requested fields, name1,name2,... , supported for action: read', 'commands': ('track')}},
    'tr-query': {'[{h}--tr-query <expression>{e}]': {'description': 'query, supported for action: read, apps: qc|bugzilla|trac|jira', 'commands': ('track')}},
    'tr-order-by': {'[{h}--tr-order-by <expression>{e}]': {'description': 'record ordering, name1:direction,name2:direction,... , direction asc|desc, supported for action: read, app: qc', 'commands': ('track')}},
    'tr-limit': {'[{h}--tr-limit <num>{e}]': {'description': 'limit, supported for action: read, apps: qc|bugzilla|jira', 'commands': ('track')}},
    'tr-offset': {'[{h}--tr-offset <num>{e}]': {'description': 'offset, supported for action: read, apps: qc|bugzilla|jira', 'commands': ('track')}},
    'tr-page': {'[{h}--tr-page <num>{e}]': {'description': 'record page, supported for action: read, app: mantis', 'commands': ('track')}},
    'tr-per-page': {'[{h}--tr-per-page <num>{e}]': {'description': 'records per page, supported for action: read, app: mantis', 'commands': ('track')}},
    'tr-params': {'[{h}--tr-params <dict>{e}]': {'description': 'record parameters, name1:value,name2:value,... , supported for actions: create|update', 'commands': ('track')}},
    'tr-path': {'[{h}--tr-path <path>{e}]': {'description': 'directory path, dir1/dir2/... , supported for use cases: read/create folder|read/create test set|create test|read/create suite, apps: qc|testlink', 'commands': ('track')}},
    'tr-steps': {'[{h}--tr-steps <list>{e}]': {'description': 'test steps delimited by |, step parameters use dictionary form, name1:value,name2:value,...|name1:value,name2:value,... , supported for action: create, app: testlink', 'commands': ('track')}},

    # standalone with option profile trackapps
    'app': {'{h}--app qc|bugzilla|mantis|trac|testlink{e}': {'description': 'application', 'commands': ('run')}},
    'action': {'{h}--action read|create|update|delete{e}': {'description': 'action, delete supported for apps: qc|mantis|trac', 'commands': ('run')}},
    'type': {'[{h}--type defect|test-folder|test|test-set-folder|test-set|test-instance|test-suite|test-plan|build{e}]': {'description': 'entity type, default defect, supported for actions: read|create|update|delete, apps: qc|testlink', 'commands': ('run')}},
    'input': {'[{h}--input <filename>{e}]': {'description': 'filename, content is written to ticket description, supported for actions: create|update', 'commands': ('run')}},
    'output': {'[{h}--output <filename>{e}]': {'description': 'filename, writes action output, supported for action: read', 'commands': ('run')}},
    'url': {'[{h}--url <url>{e}]': {'description': 'url, configurable', 'commands': ('run')}},
    'user': {'[{h}--user <username>{e}]': {'description': 'username, configurable', 'commands': ('run')}},
    'passw': {'[{h}--passw <password>{e}]': {'description': 'password, configurable', 'commands': ('run')}},
    'dev-key': {'[{h}--dev-key <key>{e}]': {'description': 'developer key, configurable, supported for app: testlink', 'commands': ('run')}},
    'domain': {'[{h}--domain <domain>{e}]': {'description': 'domain, configurable, supported for app: qc', 'commands': ('run')}},
    'project': {'[{h}--project <project>{e}]': {'description': 'project, configurable, supported for apps: qc|mantis|trac|jira|testlink', 'commands': ('run')}},
    'id': {'[{h}--id <num>{e}]': {'description': 'record id, supported for actions: read|update|delete', 'commands': ('run')}},
    'fields': {'[{h}--fields <list>{e}]': {'description': 'requested fields, name1,name2,... , supported for action: read', 'commands': ('run')}},
    'query': {'[{h}--query <expression>{e}]': {'description': 'query, supported for action: read, apps: qc|bugzilla|trac|jira', 'commands': ('run')}},
    'order-by': {'[{h}--order-by <expression>{e}]': {'description': 'record ordering, name1:direction,name2:direction,... , direction asc|desc, supported for action: read, app: qc', 'commands': ('run')}},
    'limit': {'[{h}--limit <num>{e}]': {'description': 'limit, supported for action: read, apps: qc|bugzilla|jira', 'commands': ('run')}},
    'offset': {'[{h}--offset <num>{e}]': {'description': 'offset, supported for action: read, apps: qc|bugzilla|jira', 'commands': ('run')}},
    'page': {'[{h}--page <num>{e}]': {'description': 'record page, supported for action: read, app: mantis', 'commands': ('run')}},
    'per-page': {'[{h}--per-page <num>{e}]': {'description': 'records per page, supported for action: read, app: mantis', 'commands': ('run')}},
    'params': {'[{h}--params <dict>{e}]': {'description': 'record parameters, name1:value,name2:value,... , supported for actions: create|update', 'commands': ('run')}},
    'path': {'[{h}--path <path>{e}]': {'description': 'directory path, dir1/dir2/... , supported for use cases: read/create folder|read/create test set|create test|read/create suite, apps: qc|testlink', 'commands': ('run')}},
    'steps': {'[{h}--steps <list>{e}]': {'description': 'test steps delimited by |, step parameters use dictionary form, name1:value,name2:value,...|name1:value,name2:value,... , supported for action: create, app: testlink', 'commands': ('run')}}
}
