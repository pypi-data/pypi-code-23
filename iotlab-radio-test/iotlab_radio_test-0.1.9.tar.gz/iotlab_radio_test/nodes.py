# -*- coding:utf-8 -*-


class Node(object):
    """
    Node class,

    store id, coordinates, metric values
    """

    def __init__(self, archi, node_id, network_address, x, y, z, mobile):
        self.archi = archi
        self.node_id = node_id
        self.mobile = mobile
        self.mobility_type = " "
        self.network_address = network_address
        self.state = "Alive"
        self.uid = "xxxx"
        self.x = x
        self.y = y
        self.z = z
        self.pdr = 0
        self.rssi = 0
        self.lqi = 0
        self.cluster_id = -1
