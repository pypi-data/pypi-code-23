import argparse
import os

from spaceminator.app import Spaceminator


def create_parser():
    parser = argparse.ArgumentParser(prog='spaceminator', description='spaceminator is a command line tool to help you get rid off those nasty spaces in your filenames!')
    parser.add_argument('-p', '--path', default=os.getcwd(), help='Absolute path to work on (defaults to current working directory)')
    parser.add_argument('-l', '--list', action='store_true', help='List files and directories only')
    parser.add_argument('-q', '--quiet', action='store_true', help='Disable verbose mode')
    parser.add_argument('-c', '--char', default='_', help='Replace char (default: _)')
    parser.add_argument('-r', '--recursive', action='store_true', help='Go inside directories')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--dirs-only', action='store_true', help='Rename directories only')
    group.add_argument('-f', '--files-only', action='store_true', help='Rename files only')
    group.add_argument('-ln', '--links-only', action='store_true', help='Rename symlinks only')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    file_types = {
        args.dirs_only: 'Dir',
        args.files_only: 'File',
        args.links_only: 'Symlink',
    }

    Spaceminator(
        path=args.path,
        list_only=args.list,
        quiet=args.quiet,
        char=args.char,
        recursive=args.recursive,
        file_type=file_types.get(True, None),
    ).spaceminate()


if __name__ == '__main__':
    main()
