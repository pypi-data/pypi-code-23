"""
Copyright 2017 Gu Zhengxiong <rectigu@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from logging import getLogger, basicConfig, WARNING
from argparse import ArgumentParser, RawTextHelpFormatter
import sys
import os


class Prog(object):
    """
    A minimal-complete Python command-line program.

    New in 0.2.0: A logger is available via ``self.logger``.
    """
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

        self.parser = self.make_parser()
        self.add_args()
        self.add_common_args()

        self.args = None

    def start(self):
        self.args = self.parser.parse_args()

        config = {}
        config.update(level=self.get_level())
        config.update(format=self.get_format())
        if self.args.log_file:
            config.update(filename=self.args.log_file)
            if not self.args.append_log:
                config.update(filemode='w')
        basicConfig(**config)

        self.logger.debug('args: %s', self.args)
        self.logger.debug('config: %s', config)

        try:
            self.main()
        except ExitFailure as exc:
            self.logger.error('ExitFailure: %s', exc)
            code = 1
        except Exception as exc:
            self.logger.exception('Unhandled Exception: %s', exc)
            code = 1
        else:
            code = 0
        sys.exit(code)

    def main(self):
        """
        User-defined program entry function.

        Parsed arguments are available as ``self.args``.
        """
        print('It works! Pass ``--help`` to view usage.')

    def add_args(self):
        """
        Add custom arguments to the parser here.
        The parser can be accessed with ``self.parser``.

        New in 0.2.0: You can use the shortcut ``self.add_arg``.
        """
        pass

    def add_common_args(self):
        levels_group = self.parser.add_argument_group('logging level')
        levels_group.add_argument('-v', '--verbose', action='count', default=0,
                                  help='output more logs')
        levels_group.add_argument('-q', '--quiet', action='count', default=0,
                                  help='output less logs')
        files_group = self.parser.add_argument_group('logging file')
        files_group.add_argument('--log-file',
                                 help='output logs to the file')
        files_group.add_argument('--append-log', action='store_true',
                                 help='append to instead of overwriting the file')
        try:
            self.version
        except AttributeError:
            pass
        else:
            about_group = self.parser.add_argument_group('about program')
            about_group.add_argument('--version', action='version', version=self.version)

    def get_format(self):
        fmt = 'pid: %(process)d: '
        fmt += '%(asctime)s: %(name)s: %(levelname)s: '
        fmt += '%(module)s.%(funcName)s:%(lineno)s: %(message)s'
        return fmt

    def get_level(self):
        return WARNING + (self.args.quiet-self.args.verbose)*10

    def add_arg(self, *args, **kwargs):
        """
        Shorthand for ``self.parser.add_argument``.

        New in 0.2.0.
        """
        return self.parser.add_argument(*args, **kwargs)

    def add_group(self, *args, **kwargs):
        """
        Shorthand for ``self.parser.add_argument_group``.

        New in 0.2.0.
        """
        return self.parser.add_argument_group(*args, **kwargs)

    def make_parser(self):
        """
        Create the argument parser here.
        """
        return ArgumentParser(
            description=self.desc, formatter_class=self.fmtcls, epilog=self.epilog)

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def desc(self):
        """
        ``description`` of ``ArgumentParser``.
        """
        if self.__doc__:
            desc = self.__doc__
        else:
            desc = self.name
        return desc

    @property
    def epilog(self):
        """
        ``epilog`` of ``ArgumentParser``
        """
        return None

    @property
    def fmtcls(self):
        """
        ``formatter_class`` of ``ArgumentParser``
        """
        return RawTextHelpFormatter

    @staticmethod
    def read_version(dir_path):
        if os.path.isfile(dir_path):
            dir_path = os.path.dirname(dir_path)
        base_names = ['VERSION.txt', 'VERSION', 'version.txt', 'version']
        for base_name in base_names:
            try:
                with open(os.path.join(dir_path, base_name)) as stream:
                    return stream.read().strip()
            except OSError:
                continue
        raise RuntimeError('No version file available: %s, tried %s', dir_path, base_names)


class ExitFailure(Exception):
    """
    Think it as ``EXIT_FAILURE`` from ``<stdlib.h>``.
    """
    pass
