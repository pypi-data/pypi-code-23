import logging
import argparse
from netconflib.netconf import NetConf
from sniffer import SnifferThread
from server import Server

def run():
    """Runs the configurator.
    """

    # parser
    parser = argparse.ArgumentParser(description='Network configurator.')
    parser.add_argument('--verbose', action='store_true',
                        help='print debug information (default: only info and error)')
    parser.add_argument('-sniff', action='store_true',
                        help='print packets on the network interface')
    parser.add_argument('-shells', action='store_true',
                        help='open shells to all cluster nodes')
    parser.add_argument('-shell', nargs=1, type=int,
                        help="open shell to cluster node with id")
    parser.add_argument('-ipforward', action='store_true',
                        help="enable ip forwarding on every node of the cluster")
    parser.add_argument('-updatehosts', action='store_true',
                        help="updates the hosts file of every node of the cluster")
    parser.add_argument('-ring', action='store_true',
                        help="configure the cluster's network topology as a ring")
    parser.add_argument('-star', action='store_true',
                        help="configure the cluster's network topology as a star")
    parser.add_argument('-tree', nargs=2, type=int,
                        help="configure the cluster's network topology as a tree (-tree <root> <degree>")
    parser.add_argument('--version', action='version', version='Netconf  v0.4.1')
    args = parser.parse_args()

    # logging configuration
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)
    f_handler = logging.FileHandler('app.log')
    f_handler.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler()
    if args.verbose:
        c_handler.setLevel(logging.DEBUG)
    else:
        c_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(formatter)
    c_handler.setFormatter(formatter)
    logger.addHandler(f_handler)
    logger.addHandler(c_handler)

    if args.sniff:
        server = Server()
        server.start_server()
    else:
        ncl = NetConf("config.ini")
        if args.shells:
            ncl.open_shells()
        elif args.shell is not None:
            ncl.open_shell(args.shell[0])
        elif args.ipforward:
            ncl.enable_ip_forwarding()
        elif args.updatehosts:
            ncl.update_hosts_file()
        elif args.ring:
            ncl.configure_ring_topology()
        elif args.star:
            ncl.configure_star_topology(0)
        elif args.tree is not None:
            root = args.tree[0]
            degree = args.tree[1]
            ncl.configure_tree_topology(root, degree)

if __name__ == '__main__':
    run()
