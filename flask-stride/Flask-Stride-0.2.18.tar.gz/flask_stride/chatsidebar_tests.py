import unittest
from .chatsidebar import ChatSidebar

class ChatSidebarTests(unittest.TestCase):
    def test_init(self):
        """Test the __init__() method."""
        sb = ChatSidebar(key='sidebar-key', name='My Sidebar', icon_1x='https://my.icons/1x', icon_2x='https://my.icons/2x', url='/mysidebar')

        sb_descriptor = sb.to_descriptor()
        expected = {'key': 'sidebar-key', 'name':{'value':'My Sidebar'}, 'icon':{'url':'https://my.icons/1x', 'url@2x':'https://my.icons/2x'}, 'url':'/mysidebar'}

        self.assertEqual(sb_descriptor, expected)

if __name__ == '__main__':
    unittest.main()
