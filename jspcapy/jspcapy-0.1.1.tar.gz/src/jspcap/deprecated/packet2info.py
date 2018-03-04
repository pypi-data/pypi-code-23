#/usr/bin/python3
# -*- coding: utf-8 -*-


import collections


# Packet to Info
# Convert scapy Packet to jspcap Info


from protocols import Info


def layer2info(layer):
    temp = {}
    if not getattr(layer, 'fields_desc', None):
        return

    for field in layer.fields_desc:
        value = getattr(layer, field.name)
        if value is None:
            value = None
        if not isinstance(value, Packet):
            value = layer2dict(value)
        temp[field.name] = value
    info = Info({layer.name : d})
    return info


def packet2info(packet):
    list_ = []
    count = 0
    while True:
        layer = packet.getlayer(count)
        if not layer:
            break
        list_.append(layer2info(layer))
        count += 1
    dict_ = collections.ChainMap(*list_)
    info = Info(dict(**dict_))
    return info
