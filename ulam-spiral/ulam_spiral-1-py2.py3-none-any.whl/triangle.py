import sys
from PIL import Image, ImageDraw, ImageFont

import flashtext

class Triangle:
    """Triangle

    """
    def __init__(self):
        self.font = ImageFont.truetype("FreeSansBold.ttf")
        self.map = [
            [0, 1, 0],
            [0, 0, 0],
            [3, 0, 2]
        ]
