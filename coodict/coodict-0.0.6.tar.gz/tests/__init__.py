import unittest
from coodict import CooDict

class TestCooDict(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.cd = CooDict(base={1:1, 2:2, 3:'dog'})

    def test_add(self):
        """Test adding works, and ends up in overlay."""
        self.cd[4] = 'cat'
        self.assertEqual(self.cd[4], 'cat')
        self.assertIn(4, self.cd.overlay)
        self.assertNotIn(4, self.cd.base)

    def test_repr(self):
        self.cd[4] = 'cat'
        self.assertEqual(self.cd, {1:1, 2:2, 3:'dog', 4:'cat'})

    def test_keys(self):
        self.cd[4] = 'cat'
        self.assertEqual([1,2,3,4], sorted(self.cd))

    def test_len(self):
        self.cd[4] = 'cat'
        self.assertEqual(len(self.cd), 4)

    def test_clear(self):
        """Test that overlay and deleted are cleared, but not base."""
        self.cd[4] = 'cat'
        self.cd.clear()
        self.assertEqual(len(self.cd.overlay), 0)
        self.assertEqual(len(self.cd.deleted), 0)
        self.assertTrue(len(self.cd.base) > 0)

    def test_pop_no_key(self):
        """Test that popping a non-existent key raises KeyError."""
        with self.assertRaises(KeyError) as r:
            self.cd.pop(0)

    def test_pop_base_key(self):
        """Test that popping existing key sets singleton in overlay."""
        self.cd.pop(1)
        self.assertIn(1, self.cd.deleted)

    def test_pop_overlay_key(self):
        """Test that popping overlay key just removes it."""
        self.cd[4] = 'cat'
        self.cd.pop(4)
        self.assertFalse(4 in self.cd.overlay)
        self.assertFalse(4 in self.cd.deleted)

    def test_values(self):
        self.cd[4] = 'cat'
        self.assertEqual(['1','2','cat','dog'], sorted(str(x) for x in self.cd.values()))

    def test_copy(self):
        self.cd[4] = 'cat'
        copy = self.cd.copy()
        copy[5] = 'apple'
        self.assertTrue(4 in copy)
        self.assertFalse(copy is self.cd)
        self.assertNotEqual(copy, self.cd)

if __name__ == "__main__":
    unittest.main()
