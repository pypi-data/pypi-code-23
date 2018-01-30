import netifaces
import os

import pyshark
import yaml


def apply_filter(file, filter, interface):
    packet_count = {"rx": 0, "tx": 0}
    byte_count = {"rx": 0, "tx": 0}
    for direction in ["rx", "tx"]:
        addrs = netifaces.ifaddresses(interface)
        interface_mac = addrs[netifaces.AF_LINK][0]["addr"]
        if direction == "rx":
            d_filter = filter["filter"] + " && eth.src != " + interface_mac
        else:
            d_filter = filter["filter"] + " && eth.src == " + interface_mac
        cap = pyshark.FileCapture(file, display_filter=d_filter)
        cap.load_packets()

        try:
            while True:
                packet = cap.next_packet()
                packet_count[direction] = packet_count[direction] + 1
                byte_count[direction] = byte_count[direction] + int(packet.length)
        except StopIteration as e:
            pass

    return {"bytes_tx": byte_count["tx"], "bytes_rx": byte_count["rx"], "packets_tx": packet_count["tx"],
            "packets_rx": packet_count["rx"]}


def load_filters(path):
    filter_files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    filters = []
    for file in filter_files:
        with open(file, "r") as f:
            filters.append(yaml.load(f.read()))
    return filters
