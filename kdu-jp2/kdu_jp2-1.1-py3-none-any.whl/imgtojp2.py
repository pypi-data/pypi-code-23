#!/usr/bin/python3

"""Command line script for batch converting images to JPEG 2000
format."""

import argparse
import logging

import iproc


DESCRIPTION = 'batch convert images to JPEG 2000'
FORCE_HELP = 'overwrite existing converted images'
IN_DIR_HELP = 'input directory of images'
LOG_FILE = 'imgtojp2.log'
LOSSLESS_HELP = 'use a lossless conversion'
OUT_DIR_HELP = 'output directory for images'
PROGRESS_HELP = 'show progress bar during conversion'
TIFF_HELP = 'convert images to TIFF before converting to JPEG 2000'


def main ():
    logging.basicConfig(filename=LOG_FILE, format='%(levelname)s:%(message)s',
                        level=logging.INFO)
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-f', '--force', action='store_true', help=FORCE_HELP)
    parser.add_argument('-l', '--lossless', action='store_true',
                        help=LOSSLESS_HELP)
    parser.add_argument('-p', '--progress', action='store_true',
                        help=PROGRESS_HELP)
    parser.add_argument('in_dir', help=IN_DIR_HELP, metavar='IN')
    parser.add_argument('out_dir', help=OUT_DIR_HELP, metavar='OUT')
    args = parser.parse_args()
    converter = iproc.JP2Converter(args.in_dir, args.out_dir, args.force,
                                   args.progress)
    if not converter.convert(args.lossless):
        print('There were errors in the conversion; check the log at %s for details' % LOG_FILE)


if __name__ == '__main__':
    main()
