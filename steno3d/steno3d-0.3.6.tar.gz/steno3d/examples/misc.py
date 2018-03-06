"""misc.py contains miscellaneous files and components to supplement
Steno3D examples
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tempfile import NamedTemporaryFile

import png

from .base import BaseExample, exampleproperty


class Images(BaseExample):
    """Images example

    Class containing miscellaneous image files.
    """

    @exampleproperty
    def filenames(self):
        return ['metal.png',
                'woodplanks.png',
                'steno3d.png',
                'steno3d_logo_text.png',
                'licenses.txt']

    @exampleproperty
    def metal(self):
        """metal texture png"""
        return Images.fetch_data(filename='metal.png',
                                 download_if_missing=False,
                                 verbose=False)

    @exampleproperty
    def wood(self):
        """wood texture png"""
        return Images.fetch_data(filename='woodplanks.png',
                                 download_if_missing=False,
                                 verbose=False)

    @exampleproperty
    def logo(self):
        """steno3d logo png"""
        return Images.fetch_data(filename='steno3d.png',
                                 download_if_missing=False,
                                 verbose=False)

    @exampleproperty
    def logo_with_text(self):
        """steno3d logo with text png"""
        return Images.fetch_data(filename='steno3d_logo_text.png',
                                 download_if_missing=False,
                                 verbose=False)

    def text_png(text, scale=3):
        """Returns an open png image file with text written

        Only letters, numbers, -, >, and < are allowed. New lines are
        indicated by /
        """
        text = text.split('/')
        text_out = ['']
        for t in text:
            text_line = ['1', '1', '1', '1', '1']
            for letter in t:
                for i in range(5):
                    text_line[i] += LETTERS[letter.upper()][i] + '1'
            text_out += text_line
            text_out += ['']
        text_len = max([len(t) for t in text_out])
        text_out = [line + (text_len-len(line))*'1' for line in text_out]
        img = []
        for line in text_out:
            im_line = ''
            for n in line:
                im_line += scale*n
            img += scale*[im_line]
        png_file = NamedTemporaryFile('wb+', suffix='.png')
        png_writer = png.Writer(len(img[0]), len(img), greyscale=True, bitdepth=1)
        png_writer.write(png_file, img)
        png_file.seek(0)
        return png_file


class Files(BaseExample):
    """File example

    Class containing miscelaneous files
    """

    @exampleproperty
    def example_name(self):
        return 'Files'

    @exampleproperty
    def filenames(self):
        return ['square.obj']

    @exampleproperty
    def obj_file(self):
        return Files.fetch_data(filename='square.obj',
                                download_if_missing=False,
                                verbose=False)


LETTERS = {
    'A': ['11011', '10101', '01110', '00000', '01110'],
    'B': ['00001', '01110', '00001', '01110', '00001'],
    'C': ['10000', '01111', '01111', '01111', '10000'],
    'D': ['00001', '01110', '01110', '01110', '00001'],
    'E': ['00000', '01111', '00001', '01111', '00000'],
    'F': ['00000', '01111', '00001', '01111', '01111'],
    'G': ['10000', '01111', '01100', '01110', '10001'],
    'H': ['01110', '01110', '00000', '01110', '01110'],
    'I': ['10001', '11011', '11011', '11011', '10001'],
    'J': ['11101', '11101', '11101', '01101', '10011'],
    'K': ['01101', '01011', '00111', '01011', '01101'],
    'L': ['01111', '01111', '01111', '01111', '00000'],
    'M': ['01110', '00100', '01010', '01110', '01110'],
    'N': ['01110', '00110', '01010', '01100', '01110'],
    'O': ['10001', '01110', '01110', '01110', '10001'],
    'P': ['00001', '01110', '00001', '01111', '01111'],
    'Q': ['10001', '01110', '01110', '01101', '10010'],
    'R': ['00001', '01110', '00001', '01101', '01110'],
    'S': ['10000', '01111', '10001', '11110', '00001'],
    'T': ['00000', '11011', '11011', '11011', '11011'],
    'U': ['01110', '01110', '01110', '01110', '10001'],
    'V': ['01110', '01110', '10101', '10101', '11011'],
    'W': ['01010', '01010', '01010', '10101', '10101'],
    'X': ['01110', '10101', '11011', '10101', '01110'],
    'Y': ['01110', '10101', '11011', '11011', '11011'],
    'Z': ['00000', '11101', '11011', '10111', '00000'],
    '1': ['11011', '10011', '11011', '11011', '10001'],
    '2': ['10011', '01101', '11011', '10111', '00001'],
    '3': ['00011', '11101', '10011', '11101', '00011'],
    '4': ['11001', '10101', '01101', '00001', '11101'],
    '5': ['00001', '01111', '00001', '11101', '00011'],
    '6': ['10011', '01111', '00011', '01101', '10011'],
    '7': ['00001', '11101', '11011', '11011', '11011'],
    '8': ['10011', '01101', '10011', '01101', '10011'],
    '9': ['10011', '01101', '10001', '11101', '10011'],
    '0': ['10001', '01110', '01010', '01110', '10001'],
    '-': ['11111', '11111', '00000', '11111', '11111'],
    '>': ['01111', '10111', '11011', '10111', '01111'],
    '<': ['11110', '11101', '11011', '11101', '11110'],
    ' ': ['11111', '11111', '11111', '11111', '11111'],
}

