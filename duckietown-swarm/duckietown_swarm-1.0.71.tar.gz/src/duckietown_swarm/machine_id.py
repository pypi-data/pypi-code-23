from duckietown_swarm.udp_interface import get_mac_addresses
from duckietown_swarm.utils import pretty_print_dictionary

if __name__ == '__main__':
    addresses = get_mac_addresses()
    print pretty_print_dictionary(addresses)