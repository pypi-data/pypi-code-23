from .config import Configuration
from .file_finder import FileFinder
from .converto import Converto

import logging
import argparse


def main():
    args = parse_args()
    setup_logging(args.debug)
    configuration = Configuration(args.config)
    logging.debug(configuration)
    converto = Converto(configuration, args.input)
    converto.show_main_menu()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action='store_true', help="Show debugging information")
    parser.add_argument("-c", "--config", default=None, help="Specify Configuration File Path")
    parser.add_argument("-i", "--input", default=None, help="specify the file, or the directory of files, to operate on")
    args = parser.parse_args()
    return args

def setup_logging(debug):
    if debug:
        lvl = logging.DEBUG
    else:
        lvl = logging.INFO
    logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    main()
