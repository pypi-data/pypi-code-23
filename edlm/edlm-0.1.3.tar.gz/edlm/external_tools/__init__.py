# coding=utf-8
"""
EDLM external tools
"""

# noinspection PyProtectedMember
from .miktext._miktext import MikTex
# noinspection PyProtectedMember
from .pandoc._pandoc import Pandoc

MIKTEX = MikTex()
PANDOC = Pandoc()
