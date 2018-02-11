import os.path
import re
from subprocess import Popen, PIPE
import pytest


@pytest.fixture()
def clipboard():
    """Retrieve clipboard content."""
    def callback(raw: bool=False) -> str:
        process = Popen(['osascript', '-e', u'the clipboard as \xabclass HTML\xbb'], stdout=PIPE)
        text = process.communicate()[0].decode('utf-8')
        if raw:
            return text
        hex_text = re.match(r'\xabdata HTML(.*)\xbb', text).group(1)
        return bytes.fromhex(hex_text).decode('utf-8')
    return callback


@pytest.fixture()
def resource():
    """Retrieve path to test resource file."""
    resource_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

    def callback(*paths: str) -> str:
        return os.path.join(resource_dir, *paths)
    return callback
