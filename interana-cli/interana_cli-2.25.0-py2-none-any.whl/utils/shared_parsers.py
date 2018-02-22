# Copyright 2017 Interana, Inc.
import argparse

from interana._version import __version__


def add_subcommand_subparser(p, name, help=None, example_command=None):
    '''
    Adds a subparser to a subcommand's parser. Adds another level to the command to allow for more
    complex functionality within a subcommand. First used with ia table create:
    - ia table create event
    - ia table create lookup
    - ia table create config-file

    Argument:
        p: subparser - subparser created by add_subparsers

    Example:
    my_subparser = parser.add_subparsers(help='This is a subparser.', dest='subparser_name')
    add_subcommand_subparser(my_subparser,
        'a_sub_command',
        help='This creates a new option: a_sub_command',
        example_config='ia command subcommand a_sub_command'
    )
    '''
    subcommand_subparser = p.add_parser(name, help=help, add_help=False)
    add_custom_help(subcommand_subparser)
    g = subcommand_subparser.add_argument_group("Generic")
    add_verbose_errors(g)
    add_unsafe_ssl(g)
    add_credential_handle(g)
    add_version(g)
    add_output_parameters(g)
    if example_command:
        subcommand_subparser.formatter_class = argparse.RawTextHelpFormatter
        subcommand_subparser.description = 'Example Command\n\n{}'.format(example_command)
    return subcommand_subparser


def add_verbose_errors(p):
    '''Add verbose error logging (stacktraces)

    Almost every command should use this.
    '''
    p.add_argument(
        '-v',
        '--verbose',
        help='More output e.g. stacktraces on errors.',
        action='store_true'
    )


def add_output_parameters(p):
    '''Add output option

    Any command that can generate/display output should probably use this
    '''
    p.add_argument(
        '--output',
        help='Set output format. Default is "table".',
        choices=['json', 'text', 'table'],
        default='table',
        type=str
    )


def add_credential_handle(p):
    '''Allow a command to be run against the non-default instance

    Almost every command should use this.
    '''
    p.add_argument(
        '--instance-name',
        metavar='handle',
        help='Use specific stored credential instead of default.',
        default='default'
    )


def add_unsafe_ssl(p):
    '''Allow commands to skip SSL certificat verification'''
    p.add_argument(
        '--unsafe',
        dest='unsafe_ssl',
        help='Do not verify SSL certs. DEV ONLY! DANGER!',
        action='store_true'
    )


def add_run_mode(p):
    '''Adds run mode for modules that defaults to dry-run (most deletes on data).'''
    p.add_argument(
        '--run',
        '-r',
        help='Use to execute command (dry run is default).',
        action='store_const',
        const=1,
        default=0,
    )


def add_version(p):
    '''Adds version flag to display CLI version, i.e. ia 0.1.0'''
    p.add_argument(
        '--version',
        action='version',
        help='Show program\'s version number and exit.',
        version='%(prog)s {version}'.format(version=__version__)
    )


def add_example_config(p):
    '''Adds example-config option to display a sample config file for the command.'''
    p.add_argument(
        '--example-config',
        help='Display an example config file for the command.',
        action='store_true'
    )


def add_custom_help(p):
    ''' Overriding help option's help message to remain consistent with other help message formatting'''
    p.add_argument(
        '-h',
        '--help',
        action='help',
        help='Show this help message and exit.',
        default=argparse.SUPPRESS
    )


def add_non_interactive_mode(p):
    ''' Does not require the user answer "y" to interactive prompts'''
    p.add_argument(
        '-y',
        '--yes',
        action='store_true',
        help='Automatic yes to prompts; assume "yes" as answer to all prompts and run non-interactively.',
        dest='non_interactive'
    )
