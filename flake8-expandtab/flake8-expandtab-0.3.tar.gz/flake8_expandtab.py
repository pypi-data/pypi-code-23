import re

import flake8.processor

__version__ = '0.3'


class FileProcessor(flake8.processor.FileProcessor):
    indentation_regex = re.compile(r'^(\t+)')

    def read_lines(self):
        tab_spaces = ' ' * TabExpander.tab_width
        return [
            self.indentation_regex.sub(
                lambda idn: tab_spaces * len(idn.group(0)),
                line
            )
            for line in super(FileProcessor, self).read_lines()
        ]


def patch_flake8():
    flake8.processor.FileProcessor = FileProcessor


class TabExpander(object):
    name = 'expandtab'
    version = __version__
    tab_width = 0

    def __init__(self, _):
        # this needs a dummy argument
        pass

    @classmethod
    def add_options(cls, parser):
        patch_flake8()
        parser.add_option(
            '--tab-width',
            default=0,
            action='store',
            type='int',
            help='Number of spaces to expand indentation tabs to',
            parse_from_config=True
        )

    @classmethod
    def parse_options(cls, options):
        cls.tab_width = options.tab_width

    def run(self):
        pass
