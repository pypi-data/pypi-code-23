import unittest
from neviseh import EnglishText


class EnglishTextTestCase(unittest.TestCase):

    def test_base(self):
        # Class representation
        self.assertEqual(repr(EnglishText('Hello')), 'EnglishText("Hello")')
        self.assertEqual(repr(EnglishText('Hello').translate_keymap()), 'EnglishText("Hello")')

    def test_keymap(self):
        self.assertEqual(
            str(EnglishText('لخخلمث').translate_keymap()),
            'google'
        )

    def test_numbers(self):
        self.assertEqual(
            str(EnglishText('0123456789۰۱۲۳۴۵۶۷۸۹').translate_persian_numbers()),
            '01234567890123456789'
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
