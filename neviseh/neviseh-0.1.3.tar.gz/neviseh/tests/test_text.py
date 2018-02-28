import unittest
from neviseh import Text


class TextTestCase(unittest.TestCase):

    def test_base(self):
        # Class representation
        self.assertEqual(repr(Text('Hello')), 'Text("Hello")')
        self.assertEqual(repr(Text('Hello').remove_extra_spaces()), 'Text("Hello")')

    def test_normalization(self):

        # Remove extra spaces
        self.assertEqual(
            str(Text('Lorem ipsum  ').remove_extra_spaces()),
            'Lorem ipsum '
        )

        # Remove extra newlines
        self.assertEqual(
            str(Text('Lorem \n\n\n ipsum\n').remove_extra_newlines()),
            'Lorem \n ipsum\n'
        )

        # Replace three dots
        self.assertEqual(
            str(Text('Show more ...').replace_three_dots()),
            'Show more …'
        )

        # Apply all normalizations
        self.assertEqual(
            str(Text('Show more   ...').normalize()),
            'Show more …'
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
