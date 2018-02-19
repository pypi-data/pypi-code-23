import os
import re
import sys
from pathlib import Path
from functools import wraps
from configparser import ConfigParser


class DoverError(Exception):
    pass




def version_regex():
    regex = [re.compile((r'''^((__version__|version) ?= ?|v)'''
                         r'''['"]?(?P<version>(\d+)(\.\d+)(\.\d+)?)['"]?$'''), re.I),
             re.compile(r'^.* v(?P<version>\d+\.\d+(\.\d+)?) ?.*$', re.I)
    ]

    def _version_regex(input_text):
        
        for rx in regex:
            match = rx.match(input_text)
            if match:
                return match.groupdict()['version']
        return None

    return _version_regex


class VersionedFile(object):
    '''Represents a file that contains a version string in one of these basic formats:

        version = 0.0.0
        __version__ = 0.0.0
        v0.0.0

    '''

    def __init__(self):
        self.re_ver = version_regex()
        self.file_path = None 
        self.relative_path = None
        self.content = None
        self.versioned_lines = []
        self._updates = 0

    @staticmethod
    def init(file_path, root_dir):
        vfile = VersionedFile()
        vfile.file_path = file_path
        vfile.relative_path = file_path.relative_to(root_dir)
        with file_path.open('r') as fh_:
            vfile.content = fh_.readlines()
        vfile.collect_version_info()
        return vfile

    @property
    def name(self):
        return self.file_path.name

    def collect_version_info(self):
        for index, line in enumerate(self.content):
            version_str = self.re_ver(line.strip())
            if version_str:
                self.versioned_lines.append((index, line, version_str))

    def show_version_lines(self, indent=0):
        lines = []
        indentation = ' ' * indent
        for index, line, version_str in self.versioned_lines:
            lines.append('{}{}:{:0>3}  `{}`'.format(indentation, self.relative_path, index, line.strip()))
        return '\n'.join(lines)
            
    def show_version_update(self, new_version, indent=0):
        lines = []
        indentation = ' ' * indent
        for index, line, version_str in self.versioned_lines:
            lines.append('{}{}  ({} -> {})'.format(indentation, self.relative_path, version_str, new_version))
        return '\n'.join(lines)

    def update(self, new_version):
        lines = []
        for index, line, version_str in self.versioned_lines:
            self._updates += 1
            self.content[index] = line.replace(version_str, str(new_version))

    def save(self):
        if self._updates == 0:
            return
        with self.file_path.open('w') as fh_:
            fh_.write(''.join(self.content))


def find_config_file(cwd=None):
    '''Fetches a suitable configuration file to look for dover file options.

    '''
    if not cwd:
        cwd = Path.cwd()
    cfg_opts = ('.dover', '.dover.cfg', 'dover.cfg', 'setup.cfg')
    for cfg in cfg_opts:
        cfg_pth = Path(cwd, cfg)
        if cfg_pth.exists() and cfg_pth.is_file():
            return cfg_pth

    raise DoverError('Dover found no configuration files!')


def collect_versioned_files(config_file):
    config = ConfigParser()
    config.read(config_file)
    root = config_file.parent
    versioned_files = []
    for section in config.sections():
        if section.startswith('dover:file:'):
            section_file = section.split(':')[2]
            dfile = Path(root, section_file)
            if not dfile.exists():
                err_msg = 'Invalid configuration section: [{}]. Path does not exist.'
                raise DoverError(err_msg.format(section))
            versioned_files.append(VersionedFile.init(dfile, root))
    return versioned_files


class VersionMissMatchError(Exception):
    pass


def assert_versions(versioned_files):
    versions = []
    for vfile in versioned_files:
        for vline in vfile.versioned_lines:
            index, line, version_str = vline
            versions.append(version_str)
    
    canonical_version = versions.pop()
    if not all([version == canonical_version for version in versions]):
        version_list = '\n'.join([v.show_version_lines(indent=4) for v in versioned_files])
        raise VersionMissMatchError('Not all file versions match:\n\n{}'.format(version_list)) 

    return canonical_version 


def command(func):

    @wraps(func)
    def _command(*args, **kwargs):
        try:
            cfg = find_config_file()
            vfiles = collect_versioned_files(cfg)
            current_version = assert_versions(vfiles)
            kwargs['current_version'] = current_version
            return func(vfiles, *args, **kwargs)
        except DoverError as ex:
            print(str(ex))
            sys.exit(0)
        except VersionMissMatchError as ex:
            print(str(ex))
            sys.exit(1)
        except Exception as ex:
            print(ex)
            sys.exit(1)

    return _command
