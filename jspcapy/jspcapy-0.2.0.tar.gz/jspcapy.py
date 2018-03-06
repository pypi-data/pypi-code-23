#!/usr/bin/python3
# -*- coding: utf-8 -*-


import argparse
import jspcap
import os
import sys


# main module of jspcapy
# command line tool for jspcap


# version number
__version__ = '0.1.3'


# extracting label
NUMB = lambda number, protocol: f' - Frame {number:>3d}: {protocol}'


def get_parser():
    parser = argparse.ArgumentParser(prog='jspcapy', description=(
        'PCAP file extractor and formatted exporter'
    ))
    parser.add_argument('-v', '--version', action='version', version=f'{__version__}')
    parser.add_argument('fin', metavar='input-file-name',
                        help=(
                            'The name of input pcap file. If ".pcap" omits, '
                            'it will be automatically appended.'
                        ))
    parser.add_argument('-o', '--output', action='store', metavar='file-name',
                        dest='fout', help=(
                            'The name of input pcap file. If format extension '
                            'omits, it will be automatically appended.'
                        ))
    parser.add_argument('-f', '--format', action='store', metavar='format',
                        dest='format', help=(
                            'Print a extraction report in the specified output '
                            'format. Available are all formats supported by '
                            'jsformat, e.g.: json, plist, tree, xml.'
                        ))
    parser.add_argument('-j', '--json', action='store_true', default=False,
                        help=(
                            'Display extraction report as json. This will yield '
                            '"raw" output that may be used by external tools. '
                            'This option overrides all other options.'
                        ))
    parser.add_argument('-p', '--plist', action='store_true', default=False,
                        help=(
                            'Display extraction report as macOS Property List '
                            '(plist). This will yield "raw" output that may be '
                            'used by external tools. This option overrides all '
                            'other options.'
                        ))
    parser.add_argument('-t', '--tree', action='store_true', default=False,
                        help=(
                            'Display extraction report as tree view text. This '
                            'will yield "raw" output that may be used by external '
                            'tools. This option overrides all other options.'
                        ))
    parser.add_argument('-a', '--auto-extension', action='store_true', default=False,
                        help=(
                            'If output file extension omits, append automatically.'
                        ))
    parser.add_argument('-V', '--verbose', action='store_false', default=True,
                        help=(
                            'Show more information.'
                        ))
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.format:
        fmt = args.format
    elif args.json:
        fmt = 'json'
    elif args.plist:
        fmt = 'plist'
    elif args.tree:
        fmt = 'tree'
    else:
        fmt = None

    try:
        ext = jspcap.Extractor(fin=args.fin, fout=args.fout, format=fmt,
                        auto=args.verbose, extension=args.auto_extension)
    except jspcap.exceptions.FormatError:
        try:
            ext = jspcap.Extractor(fin=args.fin, fout=args.fout, format=fmt,
                            auto=args.verbose, extension=args.auto_extension)
        except jspcap.exceptions.FileError as file_error:
            fin, fout, fmt = jspcap.Extractor.make_name(args.fin, args.fout, args.format, args.auto_extension)
            os.remove(fout)
            raise file_error(f"UnsupportedFile: Unsupported file '{fin}'")
    except jspcap.exceptions.FileError as file_error:
        fin, fout, fmt = jspcap.Extractor.make_name(args.fin, args.fout, args.format, args.auto_extension)
        os.remove(fout)
        raise file_error(f"UnsupportedFile: Unsupported file '{fin}'")
    except FileNotFoundError as file_not_found_error:
        fin, fout, fmt = jspcap.Extractor.make_name(args.fin, args.fout, args.format, args.auto_extension)
        os.remove(fout)
        raise file_not_found_error(f"FileNotFoundError: No such file or directory: '{fin}'")

    if not args.verbose:
        print(f"🚨Loading file '{ext.input}'")
        for frame in ext:
            content = NUMB(ext.length, ext.protocol)
            print(content)
        print(f"🍺Report file stored in '{ext.output}'")


if __name__ == '__main__':
    sys.exit(main())
