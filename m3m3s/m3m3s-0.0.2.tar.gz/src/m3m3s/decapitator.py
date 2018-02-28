#!/usr/bin/env python3

import argparse


def add_args_to_parser(parser):
    parser.add_argument('input_string', help='the string to decap')

    return parser


def build_parser_standalone():
    parser = argparse.ArgumentParser(description="decap")
    return add_args_to_parser(parser)


def main(args):

    decapitated_string = ""
    index = 0

    for c in args.input_string:
        if index % 2 == 0:
            decapitated_string += c.upper()
        else:
            decapitated_string += c.lower()
        index += 1

    print(decapitated_string)


if __name__ == "__main__":
    args = build_parser_standalone().parse_args()
    main(args)
