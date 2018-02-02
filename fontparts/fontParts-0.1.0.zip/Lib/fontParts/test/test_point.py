import unittest
from fontParts.base import FontPartsError


class TestPoint(unittest.TestCase):

    def getPoint_generic(self):
        contour, unrequested = self.objectGenerator("contour")
        unrequested.append(contour)
        contour.appendPoint((0, 0), "move")
        contour.appendPoint((101, 202), "line")
        point = contour.points[1]
        return point, unrequested

    # ----
    # Type
    # ----

    def test_type(self):
        point, unrequested = self.getPoint_generic()
        # get
        self.assertEqual(
            point.type,
            "line"
        )
        # set: move
        point.type = "move"
        self.assertEqual(
            point.type,
            "move"
        )
        # set: curve
        point.type = "curve"
        self.assertEqual(
            point.type,
            "curve"
        )
        # set: qcurve
        point.type = "qcurve"
        self.assertEqual(
            point.type,
            "qcurve"
        )
        # set: offcurve
        point.type = "offcurve"
        self.assertEqual(
            point.type,
            "offcurve"
        )
        # set: invalid
        with self.assertRaises(FontPartsError):
            point.type = "xxx"
        with self.assertRaises(FontPartsError):
            point.type = 123