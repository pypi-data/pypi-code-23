# -*- coding: utf-8 -*-
import unittest
import filecmp
import tempfile
from ..debinterface import Hostapd


DEFAULT_CONTENT = '''
interface=wlan0
driver=nl80211
logger_syslog=-1
logger_syslog_level=2
logger_stdout=-1
logger_stdout_level=2
debug=4
#dump_file=/tmp/hostapd.dump
#ctrl_interface=/var/run/hostapd
#ctrl_interface_group=0
channel=4
hw_mode=g
macaddr_acl=0
auth_algs=3
eapol_key_index_workaround=0
eap_server=0
wpa=3
ssid=cashpad-FTED
wpa_passphrase=cashpad-GH67
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
eapol_version=1
#wme_enabled=1
#ieee80211n=1
#ht_capab=[HT40-][HT40+][SHORT-GI-40][TX-STBC][RX-STBC1][DSSS_CCK-40]
'''

DEFAULT_CONFIG = {
    'interface': 'wlan0',
    'driver': 'nl80211',

    # logs
    'logger_syslog': "-1",
    'logger_syslog_level': "2",
    'logger_stdout': "-1",
    'logger_stdout_level': "2",

    # debug
    'debug': "4",

    # wifi
    'hw_mode': 'g',

    # security goodies
    'macaddr_acl': "0",
    'eapol_key_index_workaround': "0",
    'eap_server': "0",
    'eapol_version': "1",

    # wifi auth
    'channel': "4",
    'ssid': 'cashpad-FTED',
    'wpa_passphrase': 'cashpad-GH67',
    'auth_algs': "3",
    'wpa': "3",  # WPA + WPA2. set to 2 to restrict to WPA2
    'wpa_key_mgmt': 'WPA-PSK',
    'wpa_pairwise': 'TKIP',
    'rsn_pairwise': 'CCMP'  # some windows clients may have issues with this one
}


class TestHostapd(unittest.TestCase):
    def test_read(self):
        self.maxDiff = None
        with tempfile.NamedTemporaryFile() as source:
            source.write(DEFAULT_CONTENT.encode("ascii"))
            source.flush()
            dns = Hostapd(source.name)
            dns.read()
            self.assertDictEqual(dns.config, DEFAULT_CONFIG)

    def test_write(self):
        self.maxDiff = None
        with tempfile.NamedTemporaryFile() as source:
            dns = Hostapd(source.name)
            dns._config = DEFAULT_CONFIG
            dns.write()
            source.flush()
            content = open(source.name).read().replace("\n", "")
            for line in DEFAULT_CONTENT.split("\n"):
                if not line or line == "\n":
                    continue
                if line.startswith("#"):
                    self.assertNotIn(line, content)
                else:
                    self.assertIn(line, content)

    def test_validate_valid(self):
        """Test validate with valid data"""
        dns = Hostapd("fdlkfdl")
        dns._config = DEFAULT_CONFIG
        self.assertEqual(dns.validate(), True)

    def test_backup(self):
        with tempfile.NamedTemporaryFile() as source:
            source.write(DEFAULT_CONTENT.encode("ascii"))
            source.flush()
            dns = Hostapd(source.name)
            dns.backup()
            self.assertTrue(filecmp.cmp(source.name, dns.backup_path))

    def test_restore(self):
        backup = tempfile.NamedTemporaryFile()
        conffile = tempfile.NamedTemporaryFile()
        backup.write(DEFAULT_CONTENT.encode("ascii"))
        backup.flush()
        dns = Hostapd(conffile.name, backup.name)
        dns.restore()
        try:
            self.assertTrue(filecmp.cmp(conffile.name, backup.name))
        finally:
            backup.close()
            conffile.close()
