# -*- coding: utf-8 -*-
"""Imports for easier use"""
from .adapter import NetworkAdapter
from .adapterValidation import NetworkAdapterValidation
from .dnsmasqRange import (DnsmasqRange,
                           DEFAULT_CONFIG as DNSMASQ_DEFAULT_CONFIG)
from .hostapd import Hostapd
from .interfaces import Interfaces
from .interfacesReader import InterfacesReader
from .interfacesWriter import InterfacesWriter

__version__ = '3.3.0'

__all__ = [
    'NetworkAdapter',
    'NetworkAdapterValidation',
    'DnsmasqRange',
    'DNSMASQ_DEFAULT_CONFIG',
    'Hostapd',
    'Interfaces',
    'InterfacesReader',
    'InterfacesWriter'
]
