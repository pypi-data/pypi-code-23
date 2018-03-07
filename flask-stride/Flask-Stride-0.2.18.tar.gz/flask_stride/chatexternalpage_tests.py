import unittest
from .chatexternalpage import ChatExternalPage

class ChatExternalPageTests(unittest.TestCase):
    def test_init(self):
        """Test the __init__() method."""
        ep = ChatExternalPage(key='externalpage-key', name='My External Page', url='https://my-external-service.com/stride-externalpage')

        ep_descriptor = ep.to_descriptor()
        expected = {'key': 'externalpage-key', 'name':{'value': 'My External Page'}, 'url': 'https://my-external-service.com/stride-externalpage'}

        self.assertEqual(ep_descriptor, expected)

if __name__ == '__main__':
    unittest.main()
