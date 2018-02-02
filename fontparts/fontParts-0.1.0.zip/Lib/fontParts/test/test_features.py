import unittest
from fontParts.base import FontPartsError


class TestFeatures(unittest.TestCase):

    def getFeatures_generic(self):
        features, unreferenced = self.objectGenerator("features")
        features.text = "# test"
        return features, unreferenced

    # ----
    # Text
    # ----

    def test_text(self):
        features, unreferenced = self.getFeatures_generic()
        # get
        self.assertEqual(
            features.text,
            "# test"
        )
        # set: valid
        features.text = "# foo"
        self.assertEqual(
            features.text,
            "# foo"
        )
        features.text = None
        self.assertIsNone(features.text)
        # set: invalid
        with self.assertRaises(FontPartsError):
            features.text = 123