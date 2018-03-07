'''
.. module:: entree.projects.base
.. moduleauthor:: Julien Spronck
.. created:: Feb 2018

Module creating a base class for all projects
'''

import datetime
import getopt
import os
import sys

import six
from entree.utils import (
    copy_file_structure,
    create_dirs,
    create_single_file,
    read_config,
)

__version__ = '0.0'

PROJECTS_PATH = os.path.split(__file__)[0]
# Path to the template root directory (directory containing all templates)
TEMPLATE_ROOT = os.path.join(PROJECTS_PATH, 'templates')


class ProjectBase(object):
    '''Class for each project.

    Class attributes:
        project_type (str): project type (e.g. flask)
        project_long_name (str): long name for a project (e.g. 'Large Flask')
        template_dir (str): path to the project template directory relative to
            the template root directory
        single_file (str): path to a single file that you want to create in
            single-file mode relative to the template root directory
        replace (dict, default=None): dictionary mapping template file
            names that should be replaced when creating the files. For
            example, {'unittest_py.template': 'test_project.py'}
        version (str): version number
    '''

    # Project type (typically the python module containing the class)
    project_type = ''

    # Project long name
    project_long_name = ''

    # Path to the template directory
    template_dir = ''

    # Path to a single file that you want to create in single-file mode
    single_file = None

    # Dictionary for mapping template file names to project file names
    replace = None

    # Project version
    version = __version__

    @classmethod
    def usage(cls, exit_status):
        '''
        Displays the usage/help for this project
        '''
        msg = "\nSets up a project by creating the "
        msg += "directories and starter files.\n"
        msg += "\nUsage: \n\n"
        msg += "    entree {0} ".format(cls.project_type)
        msg += "[OPTIONS] <modname>\n\n"
        msg += "Arguments:\n\n"
        msg += "    modname: the name of the project you want to start or "
        msg += "modify\n\n"
        msg += "Options:\n\n"
        msg += "    -h, --help: prints the usage of the program with possible"
        msg += "\n                options.\n\n"
        msg += "    -a, --add: adds the files to the directory specified \n"
        msg += "                with the -d option or current directory\n"
        msg += "                without creating a project directory.\n\n"
        msg += "    -d, --dir: Specifies the directory where to create\n"
        msg += "               the project files. By default, it is the\n"
        msg += "               current directory.\n\n"
        if cls.single_file:
            msg += "    -s, --single-file: creates a single file instead of\n"
            msg += "                       a complete package.\n\n"
        msg += "    -v, --version: diplays the version number.\n\n"

        six.print_(msg)
        sys.exit(exit_status)

    @classmethod
    def template_path(cls):
        '''Builds the template path based on the template root directory and the
        project template directory

        Returns:
            A string containing the full template path
        '''
        return os.path.join(TEMPLATE_ROOT, cls.template_dir)

    @classmethod
    def single_file_path(cls):
        '''Builds the single-file path based on the template root directory and
        the project relative single-file path

        Returns:
            A string containing the full singe-file path
        '''
        if cls.single_file:
            return os.path.join(TEMPLATE_ROOT, cls.single_file)
        return ''

    @classmethod
    def get_config(cls):
        '''Gets project-specific configuration
        '''
        config = read_config()
        if 'project_config' not in config:
            return config
        if cls.__name__ not in config['project_config']:
            del config['project_config']
            return config
        for key, value in config['project_config'][cls.__name__].items():
            config[key] = value
        del config['project_config']
        return config

    @classmethod
    def create_one(cls, rootdir, filename):
        '''Creates a single-file project

        Args:
            rootdir (str): the root directory
            filename (str): the file name
        '''
        if cls.single_file:
            # Read config file and set creation_date
            config = cls.get_config()
            creation_date = datetime.datetime.now()
            modname = os.path.splitext(os.path.basename(filename))[0]
            create_single_file(rootdir, filename, cls.single_file_path(),
                               config=config, creation_date=creation_date,
                               modname=modname)

    @classmethod
    def create_all(cls, rootdir, modname, partial=None, add_to_existing=False):
        '''Creates all project files and directories

        Args:
            rootdir (str): the root directory
            modname (str): the module name

        Keyword args:
            add_to_existing (bool, default=False): True if you want to add
                files without creating a project directory (add to existing
                project)
        '''
        if add_to_existing:
            projectdir = rootdir
        else:
            # Create project directory
            projectdir = os.path.join(rootdir, modname)
            create_dirs(rootdir, projectdir)

        # Read config file and set creation_date
        config = cls.get_config()
        creation_date = datetime.datetime.now()

        if partial:
            if 'partial_builds' not in config:
                raise ValueError('No `partial_builds` config parameter for '
                                 'this project type')
            if partial not in config['partial_builds']:
                raise ValueError('Unknown partial build name: '
                                 '`{0}`'.format(partial))
            partial = config['partial_builds'][partial]
            partial = [os.path.join(cls.template_path(), path)
                       for path in partial]

        files_to_ignore = []
        if 'files_to_ignore' in config:
            files_to_ignore = config['files_to_ignore']

        # Copy entire file structure from template directory to the project
        # directory
        copy_file_structure(projectdir, cls.template_path(),
                            replace=cls.replace, partial=partial,
                            files_to_ignore=files_to_ignore,
                            modname=modname, config=config,
                            creation_date=creation_date)

    @classmethod
    def main(cls, modname=''):
        '''Main program

        Keyword args:
            modname (str, default=''): module/project name
        '''

        # Parse command line options/arguments
        options = [
            ('h', 'help'),
            ('a', 'add'),
            ('d:', 'dir='),
            ('p:', 'partial='),
            ('v', 'version')
        ]
        if cls.single_file:
            options.append(('s', 'single-file'))

        short_options = ''.join(option[0] for option in options)
        long_options = [option[1] for option in options]

        try:
            opts, args = getopt.getopt(sys.argv[2:], short_options,
                                       long_options)

        except getopt.GetoptError:
            cls.usage(3)

        add_to_existing = False
        rootdir = './'
        single_file = False
        partial = None
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                cls.usage(0)
            elif opt in ("-a", "--add"):
                add_to_existing = True
            elif opt in ("-d", "--dir"):
                rootdir = arg
            elif opt in ("-p", "--partial"):
                partial = arg
            elif opt in ("-s", "--single-file"):
                single_file = True
            elif opt in ("-v", "--version"):
                six.print_('entree.projects.{0} {1}'.format(cls.project_type,
                                                            cls.version))
                sys.exit()

        if not args:
            if not modname:
                cls.usage(4)
        elif len(args) > 1:
            cls.usage(6)
        else:
            modname = args[0]

        if single_file:
            cls.create_one(rootdir, modname)
        else:
            cls.create_all(rootdir, modname, add_to_existing=add_to_existing,
                           partial=partial)
