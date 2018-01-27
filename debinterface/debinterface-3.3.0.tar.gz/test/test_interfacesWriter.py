# -*- coding: utf-8 -*-
from __future__ import print_function, with_statement, absolute_import
import os
import unittest
import tempfile
from ..debinterface import InterfacesReader, InterfacesWriter, NetworkAdapter


INF_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "interfaces.txt")

class TestInterfacesWriter(unittest.TestCase):
    def test_write_complete(self):
        """Should work"""

        options = {
            'addrFam': 'inet',
            'broadcast': '192.168.1.255',
            'name': 'eth0.99',
            'auto': True,
            'bridge-opts': {'ports': 'eth0 ath0 ath1'},
            'up': ['ifconfig ath0 down ; ifconfig ath0 up # this is a workaround',
            'iwpriv ath1 wds 1',
            'iwpriv ath1 wds_add AA:BB:CC:DD:EE:FF',
            'ifconfig ath1 down ; ifconfig ath1 up # this is a workaround'],
            'gateway': '192.168.1.1',
            'down': ["cp /etc/badaboum /etc/bigbadaboum"],
            'source': 'static',
            'netmask': '255.255.255.0',
            'address': '192.168.1.2',
            'pre-up': [
                'wlanconfig ath0 create wlandev wifi0 wlanmode ap',
                'wlanconfig ath1 create wlandev wifi0 wlanmode wds',
                'iwpriv ath0 mode 11g',
                'iwpriv ath0 bintval 1000',
                'iwconfig ath0 essid "voyage-wds" channel 1'
            ],
            'pre-down': ['ls poufff'],
            'post-down': ['wlanconfig ath0 destroy', 'wlanconfig ath1 destroy'],
            'network': '192.168.1.0',
            'unknown': {
                'wireless-mode': 'Ad-hoc',
                'wireless-channel': '1',
                'madwifi-base': 'wifi0',
                'wireless-essid': 'voyage-adhoc'
            }
        }

        expected = [
            "auto eth0.99",
            "iface eth0.99 inet static",
            "address 192.168.1.2",
            "network 192.168.1.0",
            "netmask 255.255.255.0",
            "broadcast 192.168.1.255",
            "gateway 192.168.1.1",
            "bridge_ports eth0 ath0 ath1",
            "pre-up wlanconfig ath0 create wlandev wifi0 wlanmode ap",
            "pre-up wlanconfig ath1 create wlandev wifi0 wlanmode wds",
            "pre-up iwpriv ath0 mode 11g",
            "pre-up iwpriv ath0 bintval 1000",
            """pre-up iwconfig ath0 essid "voyage-wds" channel 1""",
            "up ifconfig ath0 down ; ifconfig ath0 up # this is a workaround",
            "up iwpriv ath1 wds 1",
            "up iwpriv ath1 wds_add AA:BB:CC:DD:EE:FF",
            "up ifconfig ath1 down ; ifconfig ath1 up # this is a workaround",
            "down cp /etc/badaboum /etc/bigbadaboum",
            "pre-down ls poufff",
            "post-down wlanconfig ath0 destroy",
            "post-down wlanconfig ath1 destroy",
            "wireless-essid voyage-adhoc",
            "wireless-channel 1",
            "wireless-mode Ad-hoc",
            "madwifi-base wifi0"
        ]
        adapter = NetworkAdapter(options={})
        adapter._ifAttributes = options
        with tempfile.NamedTemporaryFile() as tempf:
            writer = InterfacesWriter([adapter], tempf.name)
            writer.write_interfaces()

            content = open(tempf.name).read().split("\n")
            for line_written, line_expected in zip(content, expected):
                self.assertEqual(line_written.strip(), line_expected)

    def test_write_complete(self):
        """Should work"""

        options = {
            'addrFam': 'inet',
            'broadcast': '192.168.0.255',
            'source': 'static',
            'name': 'eth0',
            'auto': True,
            'up': ['ethtool -s eth0 wol g'],
            'gateway': '192.168.0.254',
            'address': '192.168.0.250',
            'netmask': '255.255.255.0',
            'dns-nameservers': ['8.8.8.8'],
        }

        expected = [
            "auto eth0",
            "iface eth0 inet static",
            "address 192.168.0.250",
            "netmask 255.255.255.0",
            "broadcast 192.168.0.255",
            "gateway 192.168.0.254",
            "dns-nameservers 8.8.8.8",
            "up ethtool -s eth0 wol g",
        ]
        adapter = NetworkAdapter(options={})
        adapter._ifAttributes = options
        with tempfile.NamedTemporaryFile() as tempf:
            writer = InterfacesWriter([adapter], tempf.name)
            writer.write_interfaces()

            content = open(tempf.name).read().split("\n")
            for line_written, line_expected in zip(content, expected):
                self.assertEqual(line_written.strip(), line_expected)

    def test_supplicant_conf_write(self):
        '''Test what wpa-conf is written out.'''

        options = {
            'addrFam': 'inet',
            'source': 'dhcp',
            'name': 'wlan0',
            'auto': True,
            'wpa-conf': '/etc/wpa_supplicant/wpa_supplicant.conf'
        }

        expected = [
            "auto wlan0",
            "iface wlan0 inet dhcp",
            "wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf"
        ]
        adapter = NetworkAdapter(options)
        with tempfile.NamedTemporaryFile() as tempf:
            writer = InterfacesWriter([adapter], tempf.name)
            writer.write_interfaces()

            content = open(tempf.name).read().split("\n")
            print(content)
            for line_written, line_expected in zip(content, expected):
                self.assertEqual(line_written.strip(), line_expected)

    def test_multiDns_write(self):
        """Should work"""

        options = {
            'addrFam': 'inet',
            'broadcast': '192.168.0.255',
            'source': 'static',
            'name': 'eth0',
            'auto': True,
            'gateway': '192.168.0.254',
            'address': '192.168.0.250',
            'netmask': '255.255.255.0',
            'dns-nameservers': ['8.8.8.8', '8.8.4.4', '4.2.2.2'],
            'dns-search': ['mydomain.com', 'myotherdomain.com']
        }

        expected = [
            "auto eth0",
            "iface eth0 inet static",
            "address 192.168.0.250",
            "netmask 255.255.255.0",
            "broadcast 192.168.0.255",
            "gateway 192.168.0.254",
            "dns-nameservers 8.8.8.8 8.8.4.4 4.2.2.2",
            "dns-search mydomain.com myotherdomain.com"
        ]
        adapter = NetworkAdapter(options)
        with tempfile.NamedTemporaryFile() as tempf:
            writer = InterfacesWriter([adapter], tempf.name)
            writer.write_interfaces()

            content = open(tempf.name).read().split("\n")
            for line_written, line_expected in zip(content, expected):
                self.assertEqual(line_written.strip(), line_expected)

    def test_header_comment_no_symbol_write(self):
        """Write without symbol should work"""

        options = {
            'addrFam': 'inet',
            'source': 'dhcp',
            'name': 'eth0',
            'auto': True
        }
        header_comment = ('This is a multiple line header comment\n'
                          'without the preceding # header, it should be placed at the top\n'
                          'of the file with each line having a "# " in front.')

        expected = [
            '# This is a multiple line header comment',
            '# without the preceding # header, it should be placed at the top',
            '# of the file with each line having a "# " in front.',
            '',
            'auto eth0',
            'iface eth0 inet dhcp'
        ]

        adapter = NetworkAdapter(options=options)
        with tempfile.NamedTemporaryFile() as tempf:
            writer = InterfacesWriter([adapter], tempf.name,
                                      header_comment=header_comment)
            writer.write_interfaces()

            content = open(tempf.name).read().split("\n")
            for line_written, line_expected in zip(content, expected):
                self.assertEqual(line_written.strip(), line_expected)

    def test_header_comment_symbol_write(self):
        """Write with symbol should work"""

        options = {
            'addrFam': 'inet',
            'source': 'dhcp',
            'name': 'eth0',
            'auto': True
        }
        header_comment = ('# This is a multiple line header comment\n'
                          '# with the preceding # header, it should be placed at the top\n'
                          '# of the file with each line having a "# " in front.')

        expected = [
            '# This is a multiple line header comment',
            '# with the preceding # header, it should be placed at the top',
            '# of the file with each line having a "# " in front.',
            '',
            'auto eth0',
            'iface eth0 inet dhcp'
        ]

        adapter = NetworkAdapter(options=options)
        with tempfile.NamedTemporaryFile() as tempf:
            writer = InterfacesWriter([adapter], tempf.name,
                                      header_comment=header_comment)
            writer.write_interfaces()

            content = open(tempf.name).read().split("\n")
            for line_written, line_expected in zip(content, expected):
                self.assertEqual(line_written.strip(), line_expected)
