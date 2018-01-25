# coding: utf8

from collections import OrderedDict
from netkit.box import Box


class Bill(Box):
    header_attrs = HEADER_ATTRS = OrderedDict([
        ('magic', ('i', 1565514879)),
        ('version', ('h', 0)),
        ('flag', ('h', 0)),
        ('packet_len', ('i', 0)),
    ])
