#!/usr/bin/python

import argparse
import sys
from gpmplgen import *
import gpmplgen.__version__
import logging


def build_argparser():
    parser = argparse.ArgumentParser(description='Create playlists automatically. Version: '
                                                 + gpmplgen.__version__.__version__)
    parser.add_argument('config', type=argparse.FileType("r"), help='Config file')
    parser.add_argument('--dry-run', action='store_true', help="Don't do any actual changes")
    parser.add_argument('--delete-all-playlists', action='store_true',
                        help="Delete all generated playlists and exit immediately")
    parser.add_argument('--force', action='store_true', help="Regenerate all playlists")  # TODO: not implemented
    parser.add_argument('--db-path', action='store', help='local DB file (usually used for debugging)')
    parser.add_argument('--write-to-db', action='store_true', help='store GPM data in specified DB file and exit')
    parser.add_argument('--debug', action='store_true', help='log debug information')
    return parser


if __name__ == '__main__':
    argparser = build_argparser()
    args = argparser.parse_args()

    cfg = Config()
    cfg.fromYaml(args.config)
    cfg.fromCli(args)

    try:
        gpmplgen = GPMPlGen(cfg)
        if cfg.delete_all_playlists:
            gpmplgen.retrieve_library(get_songs=False)
            gpmplgen.cleanup_all_generated_playlists()
            sys.exit(0)
        gpmplgen.retrieve_library()
        if cfg.write_to_db:
            sys.exit(0)
        i = 0
        for playlist in cfg.playlists.keys():
            i += 1
            gpmplgen.generate_playlist(playlist, cfg.playlists[playlist])
        logging.info("Generated %d auto playlists" % i)
    except GPMPlGenException as e:
        logging.fatal(e)
        logging.fatal("Exiting...      :-(")
        sys.exit(1)
