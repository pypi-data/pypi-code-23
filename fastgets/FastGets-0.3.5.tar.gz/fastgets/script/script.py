# coding: utf8

import os
from .. import env
from ..utils import convert_path_to_name


class Script(object):

    def __init__(self):
        self.name = None
        self.path = None

    def to_api_json(self, **kwargs):
        json_dict = dict(
            name=self.name,
            path=self.path,
        )
        json_dict.update(kwargs)
        return json_dict

    @classmethod
    def get_list(cls):
        scripts = []
        for _, _, file_names in os.walk(env.SCRIPTS_DIR):
            for file_name in file_names:
                path = env.SCRIPTS_DIR + file_name
                if file_name.endswith('.py') and file_name != '__init__.py':
                    name = convert_path_to_name(path, 'script')
                    script = cls()
                    script.name = name
                    script.path = path
                    scripts.append(script)
        return scripts

    @classmethod
    def get_dict(cls):
        return {
            script.name: script
            for script in cls.get_list()
        }
