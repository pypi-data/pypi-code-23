import unittest
from coodict import CooDict

class TestCooDict(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.cd = CooDict(base={1:1, 2:2, 3:3})


    def test_add(self):
        self.cd[4] = 4
        self.assertEqual(self.cd[4], 4)

    def test_merge(self):
        self.cd[4] = 4
        self.assertEqual(self.cd.merge(), {1:1, 2:2, 3:3, 4:4})

    def test_keys(self):
        self.cd[4] = 4
        self.assertEqual([1,2,3,4], sorted(self.cd.keys()))

    def test_len(self):
        self.cd[4] = 4
        self.assertEqual(len(self.cd.keys()), 4)

    def test_clear(self):
        self.cd[4] = 4
        self.cd.clear()
        self.assertEqual(len(self.cd.overlay), 0)

    def test_pop(self):
        self.cd.pop(3)
        self.assertIsInstance(self.cd.overlay[3], CooDict.Deleted)
        self.assertFalse(3 in self.cd.keys())
        with self.assertRaises(KeyError) as r:
            self.cd[3]

    def test_values(self):
        self.cd[4] = 4
        self.assertEqual([1,2,3,4], sorted(self.cd.values()))

    def test_copy(self):
        self.cd[4] = 4
        copy = self.cd.copy()
        copy[5] = 5
        self.assertTrue(4 in copy)
        self.assertFalse(copy == self.cd)
        self.assertFalse(copy is self.cd)

if __name__ == "__main__":
    unittest.main()
