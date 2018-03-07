# encoding: utf-8

from fdutil.parse_yaml import get_default_yaml_instance
from .yaml_provider import YAMLConfig


class CommentedYAMLConfig(YAMLConfig):
    YAML = get_default_yaml_instance()
