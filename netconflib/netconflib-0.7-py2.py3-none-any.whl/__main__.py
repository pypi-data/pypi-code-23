import logging
import argparse
from .netconf import NetConf
from .server import Server
from .client import Client
from pathlib import Path
from .helper import get_my_ip
from .commands import Commands
from .commands import Paths

def main(args=None):
    """Runs the configurator.
    """

    # parser
    parser = argparse.ArgumentParser(description='Network configurator.',
                                    formatter_class=argparse.RawTextHelpFormatter)
    config_help = '''The absolute path to the config.ini file.
The configuration file indicates the nodes' ip addresses (hosts)
and the authentication that is required to login to them.

A sample config.ini file would be:
                        
[hosts]
node1=10.0.1.33
node2=10.0.1.34
node3=10.0.1.35
node4=10.0.1.36

[authentication]
username=pi
password=raspberry

[settings]
testing=no
'''
    parser.add_argument("-config", nargs=1, type=str, metavar=('CONFIG-PATH'),
                        help=config_help)
    parser.add_argument('--verbose', action='store_true',
                        help='print debug information (default: only info and error)')
    parser.add_argument('-server', nargs='?', const=10000, type=int, metavar=('PORT'),
                        help='start server for client sniffing (sepcify port with -server <PORT>, defualt: 10000)')
    parser.add_argument('-client', nargs='?', const=10000, type=int, metavar=('PORT'),
                        help='start clients for sniffing (sepcify port with -client <PORT>, defualt: 10000)')
    parser.add_argument('-sniff', nargs=2, type=str, metavar=('SERVER-ADDRESS', 'PORT'),
                        help='start sniffing on the network interface (-sniff <server address> <port>)')
    parser.add_argument('-shells', action='store_true',
                        help='open shells to all cluster nodes')
    parser.add_argument('-shell', nargs=1, type=int, metavar=('NODE-ID'),
                        help="open shell to cluster node with id")
    parser.add_argument('-ipforward', action='store_true',
                        help="enable ip forwarding on every node of the cluster")
    parser.add_argument('-sshsetup', action='store_true',
                        help="setup ssh keys for internal communication on the cluster")
    parser.add_argument('-updatehosts', action='store_true',
                        help="updates the hosts file of every node of the cluster")
    parser.add_argument('-ring', action='store_true',
                        help="configure the cluster's network topology as a ring")
    parser.add_argument('-star', action='store_true',
                        help="configure the cluster's network topology as a star")
    parser.add_argument('-tree', nargs=2, type=int, metavar=('ROOT', 'DEGREE'),
                        help="configure the cluster's network topology as a tree (-tree <root> <degree>)")
    parser.add_argument('--version', action='version', version='Netconf  v0.7')
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
        c_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(formatter)
    c_handler.setFormatter(formatter)
    logger.addHandler(f_handler)
    logger.addHandler(c_handler)

    configfile = None
    if args.config is not None:
        if not Path(args.config[0]).is_file():
            logger.error("The specified path is not a file. Exiting...")
            exit(1)
        else:
            configfile = args.config[0]
    if args.server is not None:
        server = Server(args.server)
        server.start_server()
    elif args.sniff is not None:
        client = Client((args.sniff[0], int(float(args.sniff[1]))))
        client.start_sniffer()
    else:
        ncl = NetConf(configfile)
        if args.shells:
            ncl.open_shells()
        elif args.shell is not None:
            ncl.open_shell(args.shell[0])
        elif args.ipforward:
            ncl.enable_ip_forwarding()
        elif args.sshsetup:
            ncl.set_up_cluster_ssh()
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
        elif args.client is not None:
            logger.info("Starting the clients on the cluster...")
            cmd = Commands.cmd_start_client.format(get_my_ip(), args.client)
            ncl.execute_command_on_all(cmd)

if __name__ == '__main__':
    main()
