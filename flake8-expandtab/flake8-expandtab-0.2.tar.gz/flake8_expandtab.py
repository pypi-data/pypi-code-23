import re

import flake8.processor

__version__ = '0.2'


class TabFilteredFile(object):
    indentation_regex = re.compile(r'^(\t+)')

    def __getattr__(self, attr):
        return getattr(self._file, attr)

    def __setattr__(self, attr, value):
        return setattr(self._file, attr, value)

    def __init__(self, *args, **kwargs):
        f = open(*args, **kwargs)
        object.__setattr__(self, '_file', f)

    def __enter__(self):
        self._file.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self._file.__exit__(exc_type, exc_value, traceback)

    def readline(self, *args, **kwargs):
        line = self._file.readline(*args, **kwargs)
        strtype = type(line)
        tab_spaces = strtype(' ') * TabExpander.tab_width

        if tab_spaces:
            line = self.indentation_regex.sub(
                lambda idn: tab_spaces * len(idn.group(0)), line)

        return line

    def readlines(self):
        def gen():
            while True:
                buf = self.readline()
                if not buf:
                    break
                yield buf
        return list(gen())


def patch_flake8():
    flake8.processor.open = TabFilteredFile


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
