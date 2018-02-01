#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
python eggs
    init
        Initial a new egg
    install
        Install all eggs in `eggs.txt`
    install -S section [eggs ...]
        Install `eggs` into the `section`
    install [eggs ...]
        Equals to `install -S prod [eggs ...]
    update
        Update all eggs in `eggs.txt`
    uninstall [eggs ...]
        Uninstall the given eggs
    list
        List all eggs in `eggs.txt`
    search
        Search egg
    -h
        this
"""

from argparse import ArgumentParser

from .hen import search, install, uninstall, update, init, show


def parse_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')
    parser_init = subparsers.add_parser('init', help='Initial an egg')
    parser_init.add_argument('path', nargs='?', const='.', default='.', help='egg directory')
    parser_install = subparsers.add_parser('install', help='Install python eggs')
    parser_install.add_argument('-S', '--section', nargs=1, help='Section of eggs')
    parser_install.add_argument('eggs', nargs='*', help='python eggs')
    parser_uninstall = subparsers.add_parser('uninstall', help='Uninstall eggs')
    parser_uninstall.add_argument('eggs', nargs='+', help='Python eggs')
    subparsers.add_parser('update', help='Update eggs')
    parser_list = subparsers.add_parser('list', help='List eggs')
    parser_list.add_argument('-a', '--all', nargs='?', const='all', default='', help='List all eggs')
    parser_search = subparsers.add_parser('search', help='Search eggs')
    parser_search.add_argument('eggs', nargs=1, help='Python eggs')

    args = parser.parse_args()

    if args.action == 'init':
        init(args.path)
    elif args.action == 'install':
        install(args.eggs, args.section)
    elif args.action == 'update':
        update()
    elif args.action == 'list':
        show(args.all)
    elif args.action == 'search':
        search(args.eggs)
    else:
        uninstall(args.eggs)


def main():
    parse_args()


if __name__ == '__main__':
    main()
