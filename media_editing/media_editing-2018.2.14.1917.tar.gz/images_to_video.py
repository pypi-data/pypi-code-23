#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# images_to_video                                                              #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program is a way of processing views of the ATLAS Control Room and OP   #
# Vistars pages.                                                               #
#                                                                              #
# copyright (C) 2015 William Breaden Madden                                    #
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
    -h, --help           display help message
    --version            display version and exit

    --extension=TEXT     input image files extension  [default: png]
    --soundtrack=FILE    soundtrack file              [default: None]
    --output=FILE        output video filename        [default: video.avi]
    --fps=FPS            frames per second            [default: 30]
"""

import docopt
import os
import time
import re

from   moviepy.editor import *
import propyte
import shijian

name    = "images_to_video"
version = "2018-01-17T1525Z"

def main(options):

    codec_video = "png" # "mpeg4"
    codec_audio = "libvorbis"

    extension           =       options["--extension"]
    filename_soundtrack =       options["--soundtrack"]
    filename_output     =       options["--output"]
    FPS                 = float(options["--fps"])

    list_of_image_files = shijian.find_file_sequences(
        extension = extension
    )
    print("list of image files: {list_of_image_files}".format(
        list_of_image_files = list_of_image_files
    ))
    video = ImageSequenceClip(list_of_image_files, fps = FPS)

    propyte.pause(prompt = "Press Enter to write video.")

    if filename_soundtrack == "None":
        video.write_videofile(
            filename_output,
            fps         = FPS,
            codec       = codec_video,
            audio       = False
        )
    else:
        soundtrack = AudioFileClip(filename_soundtrack)
        video = video.set_audio(soundtrack)
        video.write_videofile(
            filename_output,
            fps         = FPS,
            codec       = codec_video,
            audio_codec = codec_audio,
            audio       = True
        )

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
