"""
Manage with eggs.txt
"""
from configparser import ConfigParser

from .common import get_version
from .output import output

EGGS_TXT = 'eggs.txt'


class Basket:
    def __init__(self):
        self.config = ConfigParser()

    def open(self):
        self.config.read(EGGS_TXT)

    def close(self):
        with open(EGGS_TXT, 'w') as f:
            self.config.write(f)
        self.show()

    def sections(self):
        return self.config.sections()

    def section(self, section):
        return self.config[section] if section in self.config else None

    def section_of(self, egg):
        for s in self.config.sections():
            if egg in self.config[s]:
                return s
        return None

    def add(self, eggs, results, section):
        for egg in eggs:
            egg = egg.split('==')[0].lower()
            index = self.section_of(egg)
            if index:
                self.config[index].pop(egg, None)
                if not self.config[index]:
                    del self.config[index]
            if section not in self.config:
                self.config[section] = {}
            self.config[section][egg] = get_version(results, egg)

    def remove(self, eggs):
        for egg in eggs:
            egg = egg.split('==')[0].lower()
            index = self.section_of(egg)
            if index:
                self.config[index].pop(egg, None)
                if not self.config[index]:
                    del self.config[index]

    def update(self, eggs, results):
        for egg in eggs:
            egg = egg.split('==')[0].lower()
            index = self.section_of(egg)
            self.config[index][egg] = get_version(results, egg)

    def show(self):
        self.open()
        items = []
        for section in self.config.sections():
            eggs = ['[{}]'.format(section)]
            eggs += ['{0} = {1}'.format(key, value) for key, value in self.config[section].items()]
            items.append('\n'.join(eggs))
        result = '\n\n'.join(items)
        output(result)
