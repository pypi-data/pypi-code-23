""" Provide tools to work with ASCII-art images and videos.

    It provides classes and functions for manipulating ASCII-art.
    Really it should work with any unicode text (not just ASCII),
    so long as every character is rendered with the same width.
"""

from .asciiimage import ASCIIImage
from .asciivideo import ASCIIVideo
from .sprite import Sprite
