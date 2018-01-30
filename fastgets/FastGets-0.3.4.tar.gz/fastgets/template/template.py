# coding: utf8

import os
import importlib.util

from .. import env
from ..utils import convert_path_to_name
from . import TemplateBase


class Template(object):

    def __init__(self):
        self.name = None
        self.path = None
        self.description = None
        self.cls = None

    def to_api_json(self, **kwargs):
        json_dict = dict(
            name=self.name,
            description=self.description,
        )
        json_dict.update(kwargs)
        return json_dict

    @classmethod
    def _find_cls(cls, name, path):
        spec = importlib.util.spec_from_file_location('_templates.{}'.format(name), path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        for attr in dir(mod):
            template = getattr(mod, attr)
            if not hasattr(template, '__bases__'):
                continue
            if TemplateBase in template.__bases__:
                return template

    @classmethod
    def get_list(cls):
        templates = []
        for _, _, file_names in os.walk(env.TEMPLATES_DIR):
            for file_name in file_names:
                path = env.TEMPLATES_DIR + file_name
                if file_name.endswith('.py') and file_name != '__init__.py':
                    name = convert_path_to_name(path, 'template')
                    cls_ = cls._find_cls(name, path)
                    if cls_:
                        template = Template()
                        template.name = name
                        template.path = path
                        template.description = (cls_.__doc__ or '').strip()
                        template.cls = cls_
                        templates.append(template)
        return templates

    @classmethod
    def get_dict(cls):
        return {
            template.name: template
            for template in cls.get_list()
        }
