import unittest
import doctest


class DocTests (unittest.TestCase):
    def test_docstrings(self):
        (failures, total) = doctest.testfile('../../README.rst')
        self.assertGreater(total, 0)
        self.assertEqual(failures, 0)
