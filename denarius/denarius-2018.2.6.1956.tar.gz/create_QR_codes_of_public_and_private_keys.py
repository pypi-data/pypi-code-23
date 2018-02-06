#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# create_QR_codes_of_public_and_private_keys                                   #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program creates a QR code for a specified public key and private key    #
# and enables optional specification of the size of the resulting PNG images.  #
# This program loads the keys from a Python file (keys.py by default) which    #
# defines the string variables key_public and key_private.                     #
#                                                                              #
# copyright (C) 2017 Will Breaden Madden, wbm@protonmail.ch                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help       display help message
    --version        display version and exit

    --size=INT       width and height in pixels of QR codes  [default: 602]
    --keys=FILEPATH  keys file                               [default: keys.py]
"""

import docopt
import os
import PIL.Image

import pyqrcode

name    = "create_QR_codes_of_public_and_private_keys"
version = "2018-01-09T2013Z"
logo    = None

def main(options):

    filepath_keys = options["--keys"]
    size          = int(options["--size"])

    filepath_keys = os.path.expanduser(filepath_keys)

    if os.path.isfile(filepath_keys):

        with open(filepath_keys, "r") as file_keys:
            file_string = file_keys.read()
            keys = {}
            exec(file_string, keys)
            key_public  = keys["key_public"]
            key_private = keys["key_private"]

        if key_public:
            qr = pyqrcode.create(key_public)
            qr.png("key_public.png", scale = 50, quiet_zone = 0)
            resize_image(filename = "key_public.png", size = size)

        if key_private:
            qr = pyqrcode.create(key_private)
            qr.png("key_private.png", scale = 50, quiet_zone = 0)
            resize_image(filename = "key_private.png", size = size)

    else:

        print("no keys file {filepath_keys} found".format(filepath_keys = filepath_keys))
        sys.exit()

def resize_image(
    filename = None,
    size     = 602
    ):

    image    = PIL.Image.open(filename)
    fraction = size / float(image.size[0])
    hsize    = int(float(image.size[1]) * float(fraction))
    image    = image.resize((size, hsize), PIL.Image.ANTIALIAS)
    image.save(filename) 

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
