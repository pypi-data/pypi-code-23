import unittest
from .chatactiontarget import ChatActionTarget

class ChatActionTargetTests(unittest.TestCase):
    def test_callService(self):
        """Test creation of a callService target."""
        at = ChatActionTarget(key='actiontarget-key', target='callService', parameters={'url': 'my-action-target-service'})

        at_descriptor = at.to_descriptor()
        expected = {'key': 'actiontarget-key', 'callService':{'url':'my-action-target-service'}}

        self.assertEqual(at_descriptor, expected)

    def test_openConfiguration(self):
        """Test creation of a openConfiguration target."""
        at = ChatActionTarget(key='actiontarget-key', target='openConfiguration', parameters={'key': 'config-key'})

        at_descriptor = at.to_descriptor()
        expected = {'key': 'actiontarget-key', 'openConfiguration':{'key':'config-key'}}

        self.assertEqual(at_descriptor, expected)

    def test_openDialog(self):
        """Test creation of a openDialog target."""
        at = ChatActionTarget(key='actiontarget-key', target='openDialog', parameters={'key': 'dialog-key'})

        at_descriptor = at.to_descriptor()
        expected = {'key': 'actiontarget-key', 'openDialog':{'key':'dialog-key'}}

        self.assertEqual(at_descriptor, expected)

    def test_openExternalPage(self):
        """Test creation of a openExternalPage target."""
        at = ChatActionTarget(key='actiontarget-key', target='openExternalPage', parameters={'key': 'external-page-key'})

        at_descriptor = at.to_descriptor()
        expected = {'key': 'actiontarget-key', 'openExternalPage':{'key':'external-page-key'}}

        self.assertEqual(at_descriptor, expected)

    def test_openSidebar(self):
        """Test creation of a openSidebar target."""
        at = ChatActionTarget(key='actiontarget-key', target='openSidebar', parameters={'key': 'sidebar-key'})

        at_descriptor = at.to_descriptor()
        expected = {'key': 'actiontarget-key', 'openSidebar':{'key':'sidebar-key'}}

        self.assertEqual(at_descriptor, expected)



if __name__ == '__main__':
    unittest.main()
