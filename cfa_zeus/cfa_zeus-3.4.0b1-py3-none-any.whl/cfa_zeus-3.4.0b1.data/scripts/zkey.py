#!python
# coding: utf8
#-----------------------------------------------------------------
# zeus: zkey.py
#
# manipulate zeus secret keys
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import argparse
import zeus

parser = argparse.ArgumentParser(description='create zeus secret keys')
parser.add_argument("--version", action='version', version='%(prog)s ' + zeus.__version__)
parser.add_argument("--size", type=int, help="size of the key in bytes (default 4096)")
parser.add_argument('outfile', help="destination key file")
args = parser.parse_args()

cipher = zeus.crypto.Vigenere(gen_key = args.outfile,
                              key_size = args.size)
