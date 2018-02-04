import argparse
import sys

from . import efile


def main():
    parser = argparse.ArgumentParser(prog='hizip', description='')
    parser.add_argument('-e', action='store_true', help='encode')
    parser.add_argument('-d', action='store_true', help='decode')
    parser.add_argument('-l', action='store_true', help='list name')
    parser.add_argument('f', help='file/dir')

    args = parser.parse_args()
    args = parser.parse_args()
    efile.main(args)


if __name__ == '__main__':
    sys.exit(main())
