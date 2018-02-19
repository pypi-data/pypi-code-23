import os
import sys
from ruamel.yaml import YAML
import comoda


def load(filename):
    yaml = YAML()
    with open(filename) as fn:
        conf = yaml.load(fn)
    return conf


class DetailsFromYamlFile:
    """
    Retrieve details from a yaml file
    """
    def __init__(self, yaml_file, loglevel='INFO'):
        self.logger = comoda.a_logger(self.__class__.__name__, level=loglevel)
        if os.path.isfile(yaml_file):
            self.conf = load(yaml_file)
        else:
            self.logger.critical('{} not exists'.format(yaml_file))
            sys.exit()

    def get_section(self, section_label):
        if self.is_section_present(section_label):
            return self.conf[section_label]
        else:
            self.logger.warning('section {} not found'.format(section_label))
            return ''

    def is_section_present(self, section_label):
        if section_label in self.conf:
            return True
        else:
            return False
