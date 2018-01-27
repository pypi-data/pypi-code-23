# -*- coding: utf-8 -*-
import unittest
from ..debinterface import NetworkAdapter


class TestNetworkAdapter(unittest.TestCase):
    def test_missing_name(self):
        """All adapters should validate"""
        adapter = NetworkAdapter({
            'addrFam': 'inet6',
            'auto': True,
            'gateway': '192.168.0.254',
            'source': 'static',
            'netmask': '255.255.255.0',
            'address': '192.168.0.250'
        })
        self.assertRaises(ValueError, adapter.validateAll)

    def test_missing_address(self):
        """All adapters should validate"""
        adapter = NetworkAdapter({
            'addrFam': 'inet',
            'name': 'eth0',
            'source': 'tunnel'
        })
        self.assertRaises(ValueError, adapter.validateAll)

    def test_bad_familly(self):
        """All adapters should validate"""
        opts = {
            'addrFam': 'inedsflkdsfst',
            'name': 'eth0',
            'source': 'tunnel'
        }
        self.assertRaises(ValueError, NetworkAdapter, opts)

    def test_assign_all_items(self):
        cmds = ['ls']
        options = {
            'name': 'wlan0',
            'addrFam': 'inet',
            'source': 'static',
            'netmask': '255.255.255.0',
            'address': '10.10.10.10',
            'gateway': '10.10.10.1',
            'broadcast': '10.10.10.255',
            'auto': True,
            'hotplug': True,
            'bridge-opts': {'maxwait': 1},
            'up' : cmds,
            'down': cmds,
            'pre-up': cmds,
            'pre-down': cmds,
            'post-down': cmds,
            'hostapd': '/etc/path/to/conf.conf',
            'dns-nameservers': '10.10.10.2 10.10.10.3',
            'dns-search': 'company.xyz',
            'wpa-conf': '/etc/wpa_supplicant/wpa_supplicant.conf'
        }

        adapter = NetworkAdapter(options=options)
        adapter.validateAll()

        self.assertEqual(adapter.attributes['name'], 'wlan0')
        self.assertEqual(adapter.attributes['addrFam'], 'inet')
        self.assertEqual(adapter.attributes['source'], 'static')
        self.assertEqual(adapter.attributes['netmask'], '255.255.255.0')
        self.assertEqual(adapter.attributes['address'], '10.10.10.10')
        self.assertEqual(adapter.attributes['gateway'], '10.10.10.1')
        self.assertEqual(adapter.attributes['broadcast'], '10.10.10.255')
        self.assertEqual(adapter.attributes['auto'], True)
        self.assertEqual(adapter.attributes['hotplug'], True)
        self.assertEqual(adapter.attributes['bridge-opts'], {'maxwait': 1})
        self.assertEqual(adapter.attributes['up'], cmds)
        self.assertEqual(adapter.attributes['down'], cmds)
        self.assertEqual(adapter.attributes['pre-up'], cmds)
        self.assertEqual(adapter.attributes['pre-down'], cmds)
        self.assertEqual(adapter.attributes['post-down'], cmds)
        self.assertEqual(adapter.attributes['hostapd'], '/etc/path/to/conf.conf')
        self.assertEqual(adapter.attributes['dns-nameservers'], '10.10.10.2 10.10.10.3')
        self.assertEqual(adapter.attributes['dns-search'], 'company.xyz')
        self.assertEqual(adapter.attributes['wpa-conf'], '/etc/wpa_supplicant/wpa_supplicant.conf')
