# -*- coding: utf-8 -*-
import os
import unittest
from ..debinterface import Interfaces


INF_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "interfaces.txt")
INF2_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "interfaces2.txt")

class TestInterfaces(unittest.TestCase):
    def test_interfaces_paths(self):
        itfs = Interfaces(interfaces_path=INF_PATH)
        self.assertEqual(itfs.interfaces_path, INF_PATH)
        self.assertEqual(itfs.backup_path, INF_PATH + ".bak")

    def test_delay_update_adapters(self):
        itfs = Interfaces(update_adapters=False, interfaces_path=INF_PATH)
        self.assertEqual(len(itfs.adapters), 0)
        itfs.updateAdapters()
        self.assertEqual(len(itfs.adapters), 10)

    def test_get_existing_adapter(self):
        itfs = Interfaces(interfaces_path=INF_PATH)
        self.assertEqual(itfs.getAdapter("eth0").attributes["name"], "eth0")

    def test_get_not_existing_adapter(self):
        itfs = Interfaces(interfaces_path=INF_PATH)
        self.assertEqual(itfs.getAdapter("eth0ddsds"), None)

    def test_add_adapter(self):
        options = {
            'addrFam': 'inet',
            'broadcast': '192.168.0.255',
            'name': 'eth9999',
            'up': ['ethtool -s eth0 wol g'],
            'gateway': '192.168.0.254',
            'down': [],
            'source': 'static',
            'netmask': '255.255.255.0',
            'address': '192.168.0.250'
        }
        itfs = Interfaces(interfaces_path=INF_PATH)
        nb_adapters = len(itfs.adapters)
        itfs.addAdapter(options)
        self.assertEqual(len(itfs.adapters), nb_adapters + 1)

    def test_add_adapter_index(self):
        options = {
            'addrFam': 'inet',
            'broadcast': '192.168.0.255',
            'name': 'eth9999',
            'up': ['ethtool -s eth0 wol g'],
            'gateway': '192.168.0.254',
            'down': [],
            'source': 'static',
            'netmask': '255.255.255.0',
            'address': '192.168.0.250'
        }
        itfs = Interfaces(interfaces_path=INF_PATH)
        nb_adapters = len(itfs.adapters)
        itfs.addAdapter(options, 4)
        self.assertEqual(len(itfs.adapters), nb_adapters + 1)
        self.assertEqual(itfs.adapters[4].attributes["name"], options["name"])

    def test_remove_adapter(self):
        itfs = Interfaces(interfaces_path=INF_PATH)
        nb_adapters = len(itfs.adapters)
        first_adapter_name = itfs.adapters[0].attributes["name"]
        itfs.removeAdapter(0)
        self.assertEqual(len(itfs.adapters), nb_adapters - 1)
        for adapter in itfs.adapters:
            self.assertNotEqual(first_adapter_name, adapter.attributes["name"])

    def test_remove_adapter_name(self):
        itfs = Interfaces(interfaces_path=INF_PATH)
        nb_adapters = len(itfs.adapters)
        itfs.removeAdapterByName("eth0")
        self.assertEqual(len(itfs.adapters), nb_adapters - 1)
        for adapter in itfs.adapters:
            self.assertNotEqual("eth0", adapter.attributes["name"])
