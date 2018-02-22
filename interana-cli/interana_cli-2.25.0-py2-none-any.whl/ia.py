#!/usr/bin/env python
# Copyright 2017 Interana, Inc.

# PYTHON_ARGCOMPLETE_OK

import argparse
import argcomplete
import requests
import logging
import random
from tabulate import tabulate
import pprint
from argparse import RawTextHelpFormatter

from commands.base import DoResult, HelpHandler
from commands.column import ColumnHandler
from commands.config import ConfigHandler
from commands.data import DataHandler
from commands.email_domain import EmailDomainHandler
from commands.job import JobHandler
from commands.lookup import LookupHandler
from commands.node import NodeHandler
from commands.pipeline import PipelineHandler
from commands.purge import PurgeHandler
from commands.settings import SettingsHandler
from commands.table import TableHandler
from commands.tier import TierHandler
from commands.user import UserHandler

from utils.shared_parsers import add_custom_help, add_version


commands = {}

description = '''

     _       _              _
    (_)_ __ | |_ ___ _ __  | |   __ _ _ __   __ _
    | | '_ \| __/ _ \ '__| | |  / _` | '_ \ / _` |
    | | | | | ||  __/ |    | | | (_| | | | | (_| |
    |_|_| |_|\__\___|_|    | |  \__,_|_| |_|\__,_|
                           |_|

    Interana: Behavioral Analytics for Event Data at Scale

'''

epilogs = [
    "When clicks hit the bricks.",
    "It's a beautiful baby cluster! 10 columns, 10 rows.",
    "Clever girl...",
    "Yeah, quidditch is stupid.",
    "Why don't we just show you a demo...",
    "I don't even know what a quail looks like.",
    "Too close for missiles, I'm switching to guns.",
    "You're in Toronto? How do you like it up there?",
    "Why don't we just hotpatch..."
]


def register_command(sps, command):
    command.parser_setup(sps)
    commands[command.name] = command


def handle_do_result(do_result, args):
    # Command should be using add_output_parameters() in shared_parsers module
    if do_result.headers:  # if tabulatable
        if not do_result.entries:
            # empty result set
            print do_result.empty_warning
        elif args.output == "json":
            formatted = [dict(zip(do_result.headers, row)) for row in do_result.entries]
            pprint.pprint(formatted)
        elif args.output == "text":
            print '\t'.join(do_result.headers)
            for row in do_result.entries:
                print '\t'.join([str(x) for x in row])
        else:  # "table":
            print tabulate(do_result.entries, headers=do_result.headers)

    # Print additional message to user.
    if do_result.message:
        print
        print do_result.message


def main():

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=RawTextHelpFormatter,
        epilog=random.choice(epilogs),
        add_help=False)

    add_version(parser)
    add_custom_help(parser)

    objects = parser.add_subparsers()

    register_command(objects, ConfigHandler())
    register_command(objects, TableHandler())
    register_command(objects, ColumnHandler())
    register_command(objects, DataHandler())
    register_command(objects, SettingsHandler())
    register_command(objects, NodeHandler())
    register_command(objects, EmailDomainHandler())
    register_command(objects, TierHandler())
    register_command(objects, JobHandler())
    register_command(objects, PipelineHandler())
    register_command(objects, PurgeHandler())
    register_command(objects, UserHandler())
    register_command(objects, HelpHandler(parser))

    # enable autocomplete
    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    if 'subcommand' in args:
        fn = commands[args.command].subcommands[args.subcommand]
    else:
        fn = commands[args.command]

    try:
        res = fn.initialize(args).do()
        if isinstance(res, DoResult):
            handle_do_result(res, args)
        elif isinstance(res, list):
            # Support lists of DoResult objects to support different output sections
            for r in res:
                if isinstance(r, DoResult):
                    handle_do_result(r, args)
                    print

    except requests.exceptions.SSLError:
        print
        print "SSL Error: could not validate identity of your host, use --unsafe only if you must"
        return 1
    except Exception as e:
        if ('verbose' in args and args.verbose) or not e.message:
            logging.traceback.print_exc(e)
            print
        if e.message:
            print 'Error:', e.message
        return 1

if __name__ == '__main__':
    exit(main())
