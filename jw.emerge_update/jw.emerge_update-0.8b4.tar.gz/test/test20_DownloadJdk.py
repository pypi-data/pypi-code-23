import unittest

from jw.emerge_update.main import JdkDownload
import sys

class TestDownloadJdk(unittest.TestCase):
    def test_downloadJdk(self):
        assert JdkDownload('jdk-8u92-linux-x64.tar.gz', output=sys.stdout)

if __name__ == '__main__':
    unittest.main()
