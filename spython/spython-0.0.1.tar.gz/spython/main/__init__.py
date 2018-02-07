#!/usr/bin/env python

'''

Copyright (C) 2017 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2016-2017 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

import argparse
import sys
import os

def get_parser():
    parser = argparse.ArgumentParser(description="Singularity Client")


    # Global Variables
    parser.add_argument('--debug', dest="debug", 
                        help="use verbose logging to debug.", 
                        default=False, action='store_true')

    parser.add_argument("--size", dest='size', 
                        help="If using legacy Singularity, specify size", 
                        type=int, default=1024)

    subparsers = parser.add_subparsers(help='actions',
                                       title='actions',
                                       description='actions for Singularity',
                                       dest="command")

    return parser


def get_subparsers(parser):
    '''get_subparser will get a dictionary of subparsers, to help with printing help
    '''

    actions = [action for action in parser._actions 
               if isinstance(action, argparse._SubParsersAction)]

    subparsers = dict()
    for action in actions:
        # get all subparsers and print help
        for choice, subparser in action.choices.items():
            subparsers[choice] = subparser

    return subparsers



def main():

    parser = get_parser()
    subparsers = get_subparsers(parser)

    try:
        args = parser.parse_args()
    except:
        sys.exit(0)

    # if environment logging variable not set, make silent
    if args.debug is False:
        os.environ['MESSAGELEVEL'] = "CRITICAL"
    
    # Always print the version
    from spython.logger import bot
    import spython
    bot.info("Singularity Python Version: %s" % spython.__version__)

    print('Still under development! Come back soon!')
    # Pass on to the correct parser
    #if args.command is not None:
    #    main(args=args,
    #         parser=parser,
    #         subparser=subparsers[args.command])
    #else:
    #    parser.print_help()


if __name__ == '__main__':
    main()
