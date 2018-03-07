import unittest

from common import get_context


class TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx = get_context()

    def test_1(self):
        faces = [
            b'\x00\x00\xff' * 4 * 4,
            b'\x00\xff\x00' * 4 * 4,
            b'\x00\xff\xff' * 4 * 4,
            b'\xff\x00\x00' * 4 * 4,
            b'\xff\x00\xff' * 4 * 4,
            b'\x00\xff\x00' * 4 * 4,
        ]
        tex = self.ctx.texture_cube((4, 4), 3, b''.join(faces))
        self.assertEqual(tex.read(0), faces[0])
        self.assertEqual(tex.read(1), faces[1])
        self.assertEqual(tex.read(2), faces[2])
        self.assertEqual(tex.read(3), faces[3])
        self.assertEqual(tex.read(4), faces[4])
        self.assertEqual(tex.read(5), faces[5])
        tex.write(0, b'\xff\xff\xff' * 4 * 4)
        self.assertEqual(tex.read(0), b'\xff\xff\xff' * 4 * 4)
        tex.write(2, b'\xff\xff\xff' * 4 * 4)
        self.assertEqual(tex.read(2), b'\xff\xff\xff' * 4 * 4)
        tex.write(5, b'\xff\xff\xff' * 4 * 4)
        self.assertEqual(tex.read(5), b'\xff\xff\xff' * 4 * 4)

    def test_2(self):
        tex = self.ctx.texture_cube((4, 4), 3)

        with self.assertRaises(Exception):
            tex.write(0, b'\xff\xff\xff' * 4 * 3)

        with self.assertRaises(Exception):
            tex.write(0, b'\xff\xff\xff' * 4 * 5)

        with self.assertRaises(Exception):
            tex.write(-1, b'\xff\xff\xff' * 4 * 4)

        with self.assertRaises(Exception):
            tex.write(6, b'\xff\xff\xff' * 4 * 4)

    def test_3(self):
        tex = self.ctx.texture_cube((4, 4), 3)

        with self.assertRaises(Exception):
            tex.read(-1)

        with self.assertRaises(Exception):
            tex.read(6)


if __name__ == '__main__':
    unittest.main()
