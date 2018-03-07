import unittest
from .chatglance import ChatGlance

class ChatGlanceTests(unittest.TestCase):
    def test_init(self):
        """Test the __init__() method."""
        gl = ChatGlance(key='glance-key', name='My Glance', icon_1x='https://my.icons/1x', icon_2x='https://my.icons/2x')

        gl_descriptor = gl.to_descriptor()
        expected = {'key': 'glance-key', 'name':{'value':'My Glance'}, 'icon':{'url':'https://my.icons/1x', 'url@2x':'https://my.icons/2x'}} 

        self.assertEqual(gl_descriptor, expected)

if __name__ == '__main__':
    unittest.main()
