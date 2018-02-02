import unittest
from fontParts.base import FontPartsError


class TestFont(unittest.TestCase):

    # ------
    # Glyphs
    # ------

    def getFont_glyphs(self):
        font, unrequested = self.objectGenerator("font")
        for name in "ABCD":
            glyph = font.newGlyph(name)
        return font, unrequested

    # len

    def test_len(self):
        font, unrequested = self.getFont_glyphs()
        # one layer
        self.assertEqual(
            len(font),
            4
        )
        # two layers
        layer = font.newLayer("test")
        layer.newGlyph("X")
        self.assertEqual(
            len(font),
            4
        )