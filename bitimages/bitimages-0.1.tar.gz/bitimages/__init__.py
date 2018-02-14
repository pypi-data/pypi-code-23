#!/usr/bin/env python
# -*- coding: utf-8 -*-

import PIL.Image
import exifread
import json
from operator import itemgetter


#  image_path = "sample.jpg"
#  Class for handling and opening a given image base on image_path
#  Handling errors is included


class ManageImage():
    def __init__(self, image_path):
        try:
            self.image = PIL.Image.open(image_path)
        except FileNotFoundError:
            raise MissingFileError
        except OSError:
            raise WrongExtensionError

    #  Function for getting height and width of a given image
    def get_size(self):
        height_width = self.image.size
        return height_width

    #  Function for getting height of a given image
    def get_height(self):
        image_height = self.image.height
        return image_height

    #  Function for getting width of a given image
    def get_width(self):
        image_width = self.image.width
        return image_width

    #  Function for getting a list of all colors in a given picture in hex
    #  system
    def get_colors(self):
        all_colors_in_hex = []
        pixels = self.image.load()
        for x in range(self.get_width()):
            for y in range(self.get_height()):
                color_rgb = pixels[x, y]
                color_hex = '#{:02x}{:02x}{:02x}'.format(color_rgb[0],
                                                         color_rgb[1],
                                                         color_rgb[2])
                all_colors_in_hex.append(color_hex)
        return all_colors_in_hex

    #  Counts the occurance of each color
    def counts_colors(self):
        colors_count = {}
        for color in self.get_colors():
            if color not in colors_count:
                colors_count[color] = 0
            else:
                colors_count[color] += 1
        return colors_count

    #  Finding the 5 most common colors in a given image
    def find_max_colors(self):
        most_common_colors = sorted(self.counts_colors().items(),
                                    key=itemgetter(1),
                                    reverse=True)[:5]
        return most_common_colors


#  Class for getting exif info (as json) if it does exist
class GetExif():
    def __init__(self, image_path):
        self.image_path = image_path
        with open(self.image_path, 'rb') as f:
            exif = exifread.process_file(f)

        exif_dict = {}

        for k in sorted(exif.keys()):
            if k not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename',
                         'EXIF MakerNote'):
                exif_dict[k] = str(exif[k])

        with open('exif_info.json', 'w') as output:
            json.dump(exif_dict, output, indent=2)


#  Exception class for handling missing files
class MissingFileError(Exception):
    def __str__(self):
        return "Given file does not exist"


#  Exception class for handling wrong extension of a given file is correct
class WrongExtensionError(Exception):
    def __str__(self):
       return "Wrong extension. Please make sure your file is an image"
