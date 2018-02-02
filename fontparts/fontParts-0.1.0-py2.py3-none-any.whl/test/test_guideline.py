import unittest
from fontParts.base import FontPartsError


class TestGuideline(unittest.TestCase):

    def getGuideline_generic(self):
        guideline, unrequested = self.objectGenerator("guideline")
        guideline.x = 1
        guideline.y = 2
        guideline.angle = 90
        return guideline, unrequested

    # --------
    # Position
    # --------

    def test_x(self):
        guideline, unrequested = self.getGuideline_generic()
        # get
        self.assertEqual(
            guideline.x,
            1
        )
        # set: valid
        guideline.x = 0
        self.assertEqual(
            guideline.x,
            0
        )
        guideline.x = 1
        self.assertEqual(
            guideline.x,
            1
        )
        guideline.x = -1
        self.assertEqual(
            guideline.x,
            -1
        )
        guideline.x = 1.1
        self.assertEqual(
            guideline.x,
            1.1
        )
        guideline.x = -1.1
        self.assertEqual(
            guideline.x,
            -1.1
        )
        # set: invalid
        with self.assertRaises(FontPartsError):
            guideline.x = "ABC"
