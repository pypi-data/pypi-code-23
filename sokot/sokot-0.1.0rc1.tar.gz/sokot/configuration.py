import datetime
import getpass
import json
import os
import sys

CONFIGURATION_MESSAGE = """
To start using sokot, run:

sokot configure
""".strip()
SOKOT_CONFIG_DIR = os.path.join(os.environ['HOME'], '.sokot')
TOKEN_PATH = os.path.join(os.environ['HOME'], '.sokot', 'token')
CONFIG_PATH = os.path.join(os.environ['HOME'], '.sokot', 'config.json')


class SokotConfiguration():
    def __init__(self):
        if not os.path.exists(SOKOT_CONFIG_DIR):
            os.mkdir(SOKOT_CONFIG_DIR)

    def _is_configured(self):
        return os.path.exists(TOKEN_PATH) and os.path.exists(CONFIG_PATH)

    def _set_token(self, token):
        f = open(TOKEN_PATH, 'w')
        f.write(token)
        f.close()

    def get_token(self):
        return self._get_token()

    def _get_token(self):
        f = open(TOKEN_PATH, 'r')
        token = f.read()
        f.close()
        return token

    def _set_config(self, config_dict):
        f = open(CONFIG_PATH, 'w')
        f.write(json.dumps(config_dict))
        f.close()

    def _get_config(self):
        if not os.path.exists(CONFIG_PATH):
            return {}
        f = open(CONFIG_PATH, 'r')
        json_str = f.read()
        f.close()
        return json.loads(json_str)

    def check(self):
        if self._is_configured():
            return self._get_token()
        print(CONFIGURATION_MESSAGE)
        sys.exit(1)

    def create(self):
        token = getpass.getpass(prompt='Token:')
        self._set_token(token)
        print("Saved to '{}'\n".format(TOKEN_PATH))

        sprint_length = int(input('Sprint Length (Default: 2):') or 2)
        scrum_start = input('The First Scrum Day (Default: 2018.01.01):') or '2018.01.01'
        config_dict = {
            'sprint_length': sprint_length,
            'scrum_start': scrum_start,
            'groups': {}
        }
        self._set_config(config_dict)
        print("Saved to '{}'".format(CONFIG_PATH))

    def get_scrum_start_day(self):
        config = self._get_config()
        date_str = config.get('scrum_start', None)
        if not date_str:
            return datetime.date.today()
        return datetime.datetime.strptime(date_str, '%Y.%m.%d').date()

    def add_group(self, name, *members):
        config = self._get_config()
        member_list = list(members)
        config['groups'][name] = member_list
        self._set_config(config)

    def delete_group(self, name):
        config = self._get_config()
        config['groups'].pop(name, None)
        self._set_config(config)

    def list_group(self):
        config = self._get_config()
        return config['groups']
