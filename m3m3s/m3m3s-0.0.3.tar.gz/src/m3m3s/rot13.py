#!/usr/bin/env python3


# usage EITHER
# ./rot13.py hello world
# echo hello world | ./rot13.py
# echo hello world | ./rot13.py | ./rot13.py # :D
# (command line "args" take presedence over stdin)

# good ole rot 13 encryption.
# I prefer the `tr "A-Z" "N-ZA-M"` version for the command line
# but wanted to mess with making a python "pipe" that could work with the system

# Also, I should write some "real" code to get my tshirt :D

# I thought about using the argparse thing from the decap script but wanted to try something different
# this means that I can't take any arguments in if I ever wanted to in the future...

import argparse


def add_args_to_parser(parser):
    parser.add_argument('input_string', help='the string to rot13')

    return parser


def build_parser_standalone():
    parser = argparse.ArgumentParser(description="rot13")
    return add_args_to_parser(parser)


ENCRYPTDICT = {}

normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
encrypted = "nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM"

ENCRYPTDICT = {plain: cipher for plain, cipher in zip(normal, encrypted)}


def encrypt(x):
    if x in ENCRYPTDICT:
        return ENCRYPTDICT[x]
    else:
        return x


def main(args):
    unencryptedString = args.input_string
    encryptedString = "".join([encrypt(x) for x in unencryptedString])

    print(encryptedString)


if __name__ == "__main__":
    args = build_parser_standalone().parse_args()
    main(args)
