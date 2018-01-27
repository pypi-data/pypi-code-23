# -*- coding: utf-8 -*-
import unittest
import socket
import copy
import filecmp
import tempfile
from ..debinterface import DnsmasqRange, DNSMASQ_DEFAULT_CONFIG


DEFAULT_CONTENT = '''
dhcp-range=interface:wlan0,10.1.10.11,10.1.10.250,24h
dhcp-range=interface:eth1,10.1.20.10,10.1.20.250,24h
#dhcp-range=interface:eth1,10.1.20.10,10.1.20.250,24h
#dhcp-range=interface:wlan0,10.1.20.10,10.1.20.250,24h
dhcp-leasefile=/var/tmp/dnsmasq.leases
'''


class TestDnsmasqRange(unittest.TestCase):
    def test_read(self):
        self.maxDiff = None
        with tempfile.NamedTemporaryFile() as source:
            source.write(DEFAULT_CONTENT.encode("ascii"))
            source.flush()
            dns = DnsmasqRange(source.name)
            dns.read()
            self.assertDictEqual(dns.config, DNSMASQ_DEFAULT_CONFIG)

    def test_write(self):
        self.maxDiff = None
        with tempfile.NamedTemporaryFile() as source:
            dns = DnsmasqRange(source.name)
            dns._config = copy.deepcopy(DNSMASQ_DEFAULT_CONFIG)
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
        dns = DnsmasqRange("fdlkfdl")
        dns._config = copy.deepcopy(DNSMASQ_DEFAULT_CONFIG)
        self.assertEqual(dns.validate(), True)

    def test_validate_invalid_ip(self):
        """Test validate with false data"""
        dns = DnsmasqRange("fdlkfdl")
        invalid = copy.deepcopy(DNSMASQ_DEFAULT_CONFIG)
        invalid["dhcp-range"][0]["start"] = "fdjfdd"
        dns._config = invalid
        with self.assertRaises(socket.error):
            dns.validate()

    def test_set(self):
        """Test set dhcp-range"""
        dns = DnsmasqRange("fdlkfdl")
        dns.set("dhcp-range", copy.deepcopy(DNSMASQ_DEFAULT_CONFIG["dhcp-range"][0]))
        nb_range = len(dns.config["dhcp-range"])
        self.assertEqual(nb_range, 1)
        self.assertDictEqual(dns.config["dhcp-range"][0], DNSMASQ_DEFAULT_CONFIG["dhcp-range"][0])

    def test_set_multiple_times(self):
        """Test set dhcp-range with many times the same value
        We should not have duplicates
        """
        dns = DnsmasqRange("fdlkfdl")
        dns.set("dhcp-range", copy.deepcopy(DNSMASQ_DEFAULT_CONFIG["dhcp-range"][0]))
        dns.set("dhcp-range", copy.deepcopy(DNSMASQ_DEFAULT_CONFIG["dhcp-range"][0]))
        nb_range = len(dns.config["dhcp-range"])
        self.assertEqual(nb_range, 1)
        self.assertDictEqual(dns.config["dhcp-range"][0], DNSMASQ_DEFAULT_CONFIG["dhcp-range"][0])

    def test_backup(self):
        with tempfile.NamedTemporaryFile() as source:
            source.write(DEFAULT_CONTENT.encode("ascii"))
            source.flush()
            dns = DnsmasqRange(source.name)
            dns.backup()
            self.assertTrue(filecmp.cmp(source.name, dns.backup_path))

    def test_restore(self):
        backup = tempfile.NamedTemporaryFile()
        conffile = tempfile.NamedTemporaryFile()
        backup.write(DEFAULT_CONTENT.encode("ascii"))
        backup.flush()
        dns = DnsmasqRange(conffile.name, backup.name)
        dns.restore()
        try:
            self.assertTrue(filecmp.cmp(conffile.name, backup.name))
        finally:
            backup.close()
            conffile.close()

    def test_extract_range_info(self):
        dns = DnsmasqRange("fdlkfdl")
        line = "dhcp-range=interface:patapan4,118.118.10.50,118.118.10.230,4h"
        info = dns._extract_range_info(line)
        expected = {
            'interface': "patapan4", 'lease_time': '4h',
            "start": "118.118.10.50", "end": "118.118.10.230"
        }
        self.assertEqual(set(expected.keys()), set(info.keys()))
        for expected_key, expected_value in expected.items():
            self.assertEqual(expected_value, info[expected_key])

    def test_update_range(self):
        dns = DnsmasqRange("fdsfddf")
        dns._config = copy.deepcopy(DNSMASQ_DEFAULT_CONFIG)
        expected = {
            "interface": 'wlan0',
            "start": '192.192.192.2',
            "end": '192.192.192.254',
            "lease_time": '24h'
        }
        dns.update_range(
            interface='wlan0',
            start='192.192.192.2',
            end='192.192.192.254',
            lease_time='24h'
        )
        cur_range = dns.get_itf_range("wlan0")
        self.assertEqual(set(expected.keys()), set(cur_range.keys()))
        for expected_key, expected_value in expected.items():
            self.assertEqual(expected_value, cur_range[expected_key])
