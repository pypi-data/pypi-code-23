# -*- coding: utf-8 -*-

import argparse
import sys
from .project.Project import Project, ProjectAlreadyExistsException


def create_parser():
    parser = argparse.ArgumentParser(
        prog="chestella",
        description="chestella: a c-project manager")

    subparser = parser.add_subparsers()

    #init command
    init_parser = subparser.add_parser('init', help='create a new project')
    init_parser.add_argument('path', help='Path of the brand new project')

    return parser


def main():
    parser = create_parser()
    #parse_args takes argumetns from sys.argv
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        raise SystemExit

    try:
        Project(args.path)
    except ProjectAlreadyExistsException as e:
        print("Oops! Something went wrong \n[{}]".format(e))


# if __name__ == "__main__":
    # main()
