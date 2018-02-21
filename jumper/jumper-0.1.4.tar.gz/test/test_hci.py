import unittest
from jumper.vlab_hci_device import VirtualHciDevice
import subprocess


class TestHci(unittest.TestCase):
    def setUp(self):
        self.hci = VirtualHciDevice()
        self.hci.start()

    def tearDown(self):
        self.hci.stop()

    def test_sanity(self):
        hciconfig_process = subprocess.Popen(['hciconfig'], stdout=subprocess.PIPE)
        hciconfig_process.wait()
        stdout, stderr = hciconfig_process.communicate()
        self.assertRegexpMatches(stdout, 'FF:05:04:03:02:FF')
