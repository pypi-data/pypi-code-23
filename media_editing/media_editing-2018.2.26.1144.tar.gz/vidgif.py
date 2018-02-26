#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# vidgif                                                                       #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program converts a video to an animated GIF.                            #
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
    -h, --help               display help message
    --version                display version and exit
    -v, --verbose            verbose logging
    -s, --silent             silent
    -u, --username=USERNAME  username

    --filename_video=TEXT    filename of input video                 [default: video.mp4]
    --filename_GIF=TEXT      filename of output GIF                  [default: video.gif]
    --directory=TEXT         directoryname for tmp                   [default: tmp]
    --delay=float            frame delay (1/100 s) (delay = 100/FPS) [default: 5]

    --display_commands_only  display commands only, do not execute
"""

from __future__ import division

import docopt
import logging
import math
import os
import sys
import uuid

import pymediainfo
import shijian
import technicolor

name     = "vidgif"
version  = "2018-02-26T1144Z"

log = logging.getLogger(name)
log.addHandler(technicolor.ColorisingStreamHandler())
log.setLevel(logging.DEBUG)

def main(options):

    filename_video        =       options["--filename_video"]
    filename_GIF          =       options["--filename_GIF"]
    directory_tmp         =       options["--directory"]
    delay                 = float(options["--delay"])
    display_commands_only =       options["--display_commands_only"]

    if not os.path.isfile(filename_video):
        print("{filename_video} not found".format(filename_video = filename_video))
        sys.exit()
    media_information = pymediainfo.MediaInfo.parse(filename_video)
    duration = int(math.ceil(media_information.tracks[0].duration / 1000))
    command =\
    """
    export MAGICK_MEMORY_LIMIT=1024
    export MAGICK_MAP_LIMIT=1024
    export MAGICK_AREA_LIMIT=4096
    export MAGICK_FILES_LIMIT=1024
    export MAGICK_THREAD_LIMIT=1
    export MAGICK_TMPDIR=/tmp

    mplayer -ao null -ss 0:00:00 -endpos {duration} {filename_video} -vo jpeg:outdir={directory_tmp}:quality=100

    #mogrify -resize 50% {directory_tmp}/*.jpg

    convert -delay {delay} -loop 0 -layers optimize {directory_tmp}/*.jpg {filename_GIF}
    """.format(
        filename_video = filename_video,
        filename_GIF   = filename_GIF,
        directory_tmp  = directory_tmp,
        duration       = duration,
        delay          = delay
    )
    log.info(command)
    if not display_commands_only:
        shijian.engage_command(command = command)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
