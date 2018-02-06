#!/usr/bin/env python

"""
################################################################################
#                                                                              #
# sound_search                                                                 #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program searches for sound files.                                       #
#                                                                              #
# copyright (C) 2015 Will Breaden Madden, w.bm@cern.ch                         #
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
    -h, --help               display help message
    --version                display version and exit
    -v, --verbose            verbose logging
    -s, --silent             silent
    -u, --username=USERNAME  username

    --minlength=SECONDS      length of sound file in seconds [default: 300]
    --extensions=EXTENSIONS  filename extensions [default: ogg,flac,wav,mp3,m3u]
    --directory=DIRECTORY    directory at which to search [default: .]
"""

import commands
import docopt
import os
import sys
import time

name    = "sound_search"
version = "2017-05-17T1932Z"
logo    = None

def main(options):

    length_minimum_specification = float(options["--minlength"])
    extensions                   = options["--extensions"].split(",")
    search_directory             = options["--directory"]

    print("\nsearch for sound files of minimum length {time} s at directory "
          "{directory} and subdirectories\n".format(
        time      = length_minimum_specification,
        directory = search_directory
    ))

    results_listing = []
    for root, directories, files in os.walk(search_directory):
        for file in files:
            for extension in extensions:
                if file.endswith(extension):
                    filename = os.path.join(root, file)
                    length = length_sound_file(filename)
                    if length is not None:
                        if float(length) >= length_minimum_specification:
                            print(filename)

def length_sound_file(filename):
    output = commands.getoutput("sox \"{filename}\" -n stat".format(
        filename = filename
    ))
    try:
        length_line = next(
            line for line in output.split("\n") if "Length" in line
        )
        length = length_line.split(":")[1].strip()
    except:
        length = None  
    return length

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
