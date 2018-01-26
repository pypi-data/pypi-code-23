#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# create_paper_wallet                                                          #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program creates a QR code for a specified public key and private key.   #
# It then creates an image of a Bitcoin paper wallet. This program loads the   #
# keys from a Python file (keys.py by default) which defines the string        #
# variables key_public and key_private.                                        #
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
    -h, --help         display help message
    --version          display version and exit

    --keys=FILEPATH    keys file          [default: keys.py]
    --wallet=FILEPATH  paper wallet file  [default: paper_wallet.png]
"""

import docopt
import os
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import re
import sys

import pyqrcode

name    = "create_paper_wallet"
version = "2017-12-25T1844Z"
logo    = None

def main(options):

    filepath_keys         = options["--keys"]
    filepath_paper_wallet = options["--wallet"]

    # QR codes

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
            resize_image(filename = "key_public.png", size = 602)

        if key_private:
            qr = pyqrcode.create(key_private)
            qr.png("key_private.png", scale = 50, quiet_zone = 0)
            resize_image(filename = "key_private.png", size = 602)

    else:

        print("no keys file {filepath_keys} found".format(filepath_keys = filepath_keys))
        sys.exit()

    # paper wallet image

    if all([
        os.path.isfile("key_public.png"),
        os.path.isfile("key_private.png"),
        os.path.isfile("Bitcoin_paper_wallet_template.png"),
        os.path.isfile("consolas.ttf"),
        os.path.isfile("FuturaLT-Light.ttf")
        ]):

        key_public_text  = "public key:\n\n"  + key_public
        key_private_text = "private key:\n\n" + key_private

        key_public_text  = hard_wrap_text(text = key_public_text,  width = 26)
        key_private_text = hard_wrap_text(text = key_private_text, width = 26)

        image_paper_wallet = PIL.Image.open("Bitcoin_paper_wallet_template.png")

        draw       = PIL.ImageDraw.Draw(image_paper_wallet)
        font_keys  = PIL.ImageFont.truetype("consolas.ttf", 42)
        font_title = PIL.ImageFont.truetype("FuturaLT-Light.ttf", 110)

        draw.text((415, 89),   "BITCOIN ADDRESS KEYS", (0, 0, 0), font = font_title)
        draw.text((51, 969),   key_public_text,        (0, 0, 0), font = font_keys)
        draw.text((1349, 969), key_private_text,       (0, 0, 0), font = font_keys)

        image_key_public  = PIL.Image.open("key_public.png")
        image_key_private = PIL.Image.open("key_private.png")

        image_paper_wallet.paste(image_key_public,  (51, 319))
        image_paper_wallet.paste(image_key_private, (1349, 319))

        image_paper_wallet.save("paper_wallet.png")

    else:

        print("missing files for creating paper wallet".format(filepath_keys = filepath_keys))
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

def hard_wrap_text(
    text  = None,
    width = None
    ):

    return re.sub(r'(.{' + str(width) + '})', '\\1\n', text)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
