#!/usr/bin/env python3

from argparse import ArgumentParser
from os import path
from sys import exit, stderr

from pbraw import grab

def main():
    parser = ArgumentParser(description='A utility to extract plaintexts from pastebins')
#    parser.add_argument('-c', '--cookies-file',
#            help='Cookies file, in the cookies.txt Netscape format')
    parser.add_argument('url', metavar='URL', nargs='+',
            help='URL to grab the plaintext from')
    args = parser.parse_args()

#    if args.file and not path.isfile(path.cookies_file):
#        print('Error: invalid cookies file provided')
#        exit(-1)

    for url in args.url:
        files = grab(url)
        if files:
            for name, contents in files:
                print('Received', name, file=stderr)
                print(str(contents), end='')
        else:
            print('Error: could not grab', url)
