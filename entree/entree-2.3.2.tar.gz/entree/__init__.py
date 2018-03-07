#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. module:: entree
.. moduleauthor:: Julien Spronck
.. created:: Apr 2015

Simple module to create files and directories in a python project
"""
import getopt
import sys

import entree.projects
import entree.utils
import six

__version__ = '2.3.2'

CLASSES = entree.projects.CLASSES


def main():
    '''Main program
    '''

    def usage(exit_status):
        '''
        Displays the usage/help of this script
        '''
        msg = "\nentree sets up starter files for different types of \n"
        msg += "programming projects.\n\n"
        msg += "\nUsage: \n\n"
        msg += "    entree [OPTIONS] <PROJECT_TYPE> [PROJECT_OPTIONS] ...\n\n"
        msg += "Arguments:\n\n"
        msg += "    PROJECT_TYPE: the type of the project you want to start\n"
        msg += "\n        Available project types:\n"
        for submodule in CLASSES:
            msg += "            - {0}: type `entree {0} -h`".format(submodule)
            msg += " for help\n"
        msg += "\nOPTIONS:\n\n"
        msg += "    -m, --modules: list available project types.\n\n"
        msg += "    -v, --version: diplays the version number.\n\n"
        msg += "PROJECT_OPTIONS:\n\n"
        msg += "    Available options are specific to each project type\n\n"

        six.print_(msg)
        sys.exit(exit_status)

    # Parse command line options/arguments
    options = [
        ('h', 'help'),
        ('m', 'modules'),
        ('v', 'version')
    ]
    short_options = ''.join(option[0] for option in options)
    long_options = [option[1] for option in options]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options,
                                   long_options)
    except getopt.GetoptError:
        usage(3)

    for opt, _ in opts:
        if opt in ("-h", "--help"):
            usage(0)
        if opt in ("-m", "--module"):
            six.print_('\nList of available modules:\n')
            for submodule in CLASSES:
                six.print_('- ' + submodule)
            six.print_()
            sys.exit()
        if opt in ("-v", "--version"):
            six.print_('entree {0}'.format(__version__))
            sys.exit()

    if not args:
        usage(4)

    submodule = args[0]

    if submodule in CLASSES:
        CLASSES[submodule].main()
    else:
        submodule = entree.utils.get_config_param('default_project_type',
                                                  'python')
        if submodule not in CLASSES:
            raise ValueError('Invalid default project type. See `entree -m` '
                             'for possible options.')
        CLASSES[submodule].main(modname=args[0])

if __name__ == '__main__':
    main()
