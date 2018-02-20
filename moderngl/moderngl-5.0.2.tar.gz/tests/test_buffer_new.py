import unittest

from common import get_context


class TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ctx = get_context()

    def test_1(self):
        buf = self.ctx.buffer(b'abc')
        self.assertEqual(buf.read(), b'abc')
        buf.write(b'xyz')
        self.assertEqual(buf.read(), b'xyz')
        self.assertEqual(buf.read(offset=1), b'yz')

    def test_2(self):
        buf = self.ctx.buffer(reserve=10)
        self.assertEqual(buf.size, 10)
        buf.write(b'12345')
        buf.write(b'abcde', offset=5)
        self.assertEqual(buf.read(5), b'12345')
        self.assertEqual(buf.read(5, offset=5), b'abcde')

    def test_3(self):
        buf = self.ctx.buffer(reserve='1KB')
        self.assertEqual(buf.size, 1024)
        buf.clear(chunk=b'u')
        self.assertEqual(buf.read(), b'u' * 1024)
        buf.clear(size=10, offset=10, chunk=b'ab')
        self.assertEqual(buf.read(10, offset=0), b'uuuuuuuuuu')
        self.assertEqual(buf.read(10, offset=10), b'ababababab')
        self.assertEqual(buf.read(10, offset=20), b'uuuuuuuuuu')

    def test_4(self):
        buf = self.ctx.buffer(reserve=10)
        buf.write_chunks(b'00000', 0, 2, 5)
        buf.write_chunks(b'11111', 1, 2, 5)
        self.assertEqual(buf.read(10, offset=0), b'0101010101')

    def test_5(self):
        buf = self.ctx.buffer(b'123456789')
        buf.write_chunks(b'AABBCC', 0, 3, 3)
        self.assertEqual(buf.read(), b'AA3BB6CC9')
        self.assertEqual(buf.read_chunks(2, 0, 3, 3), b'AABBCC')

    def test_6(self):
        buf = self.ctx.buffer(b'123456789')
        buf.write_chunks(b'XYZ', -1, -3, 3)
        self.assertEqual(buf.read(), b'12Z45Y78X')
        self.assertEqual(buf.read_chunks(1, -1, -3, 3), b'XYZ')

    def test_7(self):
        buf = self.ctx.buffer(b'123456789')
        self.assertEqual(buf.read_chunks(3, 0, 3, 3), b'123456789')

    def test_8(self):
        buf1 = self.ctx.buffer(b'abc', dynamic=True)
        buf2 = self.ctx.buffer(b'abc', dynamic=False)
        self.assertTrue(buf1.dynamic)
        self.assertFalse(buf2.dynamic)


if __name__ == '__main__':
    unittest.main()
