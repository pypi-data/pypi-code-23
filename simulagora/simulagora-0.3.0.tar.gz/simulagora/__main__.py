# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# Simulagora-client is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# This software is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

"""
This is a simple executable script that uses the simulagora.Simulagora client
class to issue simple commands directly from the console.

All the methods of this class are not usable though as those that require non
simple types as input cannot presently be called with this script.

Use -h option to get help.
"""

import sys
import logging
import argparse
from pprint import pprint
from simulagora import Simulagora  # pylint: disable=import-self


def _parse_args(stringargs):
    """ Type user arguments by trying an explicit conversion (int, float or
    string if both fail) and split them into positional or keyword arguments:
    if an argument contains the "=" sign, it will be a keyword one.
    """
    def type_arg(arg):
        """ Try to type `arg` as int then float, or return the original string.
        """
        for tested_type in int, float:
            try:
                return tested_type(arg)
            except ValueError:
                pass
        return arg
    args, kwargs = [], {}
    for stringarg in stringargs:
        if '=' in stringarg:
            key, value = stringarg.split('=', 1)
            kwargs[key] = type_arg(value)
        else:
            args.append(type_arg(stringarg))
    return args, kwargs


def main():
    """ Main entry point: parses user arguments, call the command and pretty
    prints the result.
    """
    parser = argparse.ArgumentParser(
        description='Simple client for Simulagora')
    parser.add_argument(
        '-A', '--account', type=str, nargs='?',
        default='simulagora',
        help='Account section name in your .config/cwclientlibrc file',
        metavar='ACCOUNT')
    parser.add_argument('--loglevel', type=str, nargs='?', default=None,
                        help=('Log level (one of DEBUG, INFO, '
                              'WARNING, ERROR, CRITICAL)'),
                        metavar='loglevel')
    parser.add_argument('command',
                        help='Command to be launched (one Simulagora method)')
    parser.add_argument('args', nargs=argparse.REMAINDER,
                        help=('Arguments and keyword arguments of the command.'
                              '\nExample for the find_one command:'
                              '\n%(prog)s find_one Executable name=myexec'))
    args = parser.parse_args()
    client = Simulagora.for_instance(args.account)

    method = getattr(client, args.command, None)
    if not callable(method):
        print >> sys.stderr, '%r is not a simulagora command' % args.command
        sys.exit(1)
    if args.loglevel is not None:
        logging.getLogger().setLevel(getattr(logging, args.loglevel.upper()))
    args, kwargs = _parse_args(args.args)
    result = method(*args, **kwargs)  # pylint: disable=star-args
    if result is not None:
        pprint(result)


if __name__ == '__main__':
    main()
