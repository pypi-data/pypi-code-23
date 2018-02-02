import unittest
from fontParts.base import FontPartsError


class TestBPoint(unittest.TestCase):

    def getBPoint_corner(self):
        contour, unrequested = self.objectGenerator("contour")
        unrequested.append(contour)
        contour.appendPoint((0, 0), "move")
        contour.appendPoint((101, 202), "line")
        contour.appendPoint((303, 0), "line")
        bPoint = contour.bPoints[1]
        return bPoint, unrequested

    # ----
    # Type
    # ----

    def test_type(self):
        bPoint, unrequested = self.getBPoint_corner()
        self.assertEqual(
            bPoint.type,
            "corner"
        )