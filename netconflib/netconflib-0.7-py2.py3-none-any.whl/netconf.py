# -*- coding: utf-8 -*-
"""A linux cluster configuration library.

Use this library to conveniently configure the network topology of a linux cluster.
"""

import os
import subprocess
from sys import platform
import configparser
import logging
from treelib import Tree
from paramiko import BadHostKeyException
from paramiko import AuthenticationException
from paramiko import SSHException
from .ssh import SSH
from .commands import Commands
from .commands import Paths

class NetConf:
    """Configuration library

    This class provides methods to configure the network
    of a Linux cluster.
    """

    def __init__(self, configfile=None):
        self.logger = logging.getLogger('app.netconflib.NetConf')
        self.logger.info("Starting linux network configuration...")
        self.config = self.init_config(configfile)
        nodes = self.config.items("hosts")
        num_nodes = len(nodes)
        username = self.config.get("authentication", "username")
        password = self.config.get("authentication", "password")
        self.types = TopologyTypes()
        self.topology = Topology(None, num_nodes, username, password)
        self.topology.clean_up()
        self.topology.add_nodes_from_list(nodes)

        self.testing = self.config.getboolean("settings", "testing")

        if not self.testing:
            self.topology.create_all_connections()

    def init_config(self, configfile):
        """Initializes and returns the configuration file.
        
        Arguments:
            configfile {string} -- File path to config.ini
        
        Returns:
            ConfigParser -- The configuration object.
        """

        config = configparser.ConfigParser()
        if configfile is None:
            self.create_default_config_file()
            config.read(Paths.config_file)
        else:
            config.read(configfile)
        return config
    
    def create_default_config_file(self):
        """Creates a new default config file in program folder.
        """

        config = configparser.ConfigParser()

        config['hosts'] = {'node1': '10.0.1.33',
                           'node2': '10.0.1.34',
                           'node3': '10.0.1.35',
                           'node4': '10.0.1.36'}
        config['authentication'] = {'username': 'pi',
                                    'password': 'raspberry'}
        config['settings'] = {'testing': 'no'}
        with open(Paths.config_file, 'w') as configfile:
            config.write(configfile)

    def enable_ip_forwarding(self):
        """Enables ip packet forwarding on every node on the cluster."""

        self.logger.info("Enabling IP packet forwarding...")
        for node in self.topology.nodes:
            if not self.testing and not node.connection is None:
                node.connection.send_command(Commands.cmd_ipforward)

    def update_hosts_file(self):
        """Appends all the ip addresses and host names to etc/hosts file.
        """

        for nodex in self.topology.nodes:
            for nodey in self.topology.nodes:
                nodex.add_host(nodey)

        if not self.testing:
            self.topology.send_all_hosts()

    def configure_ring_topology(self, remove=False):
        """Configures the cluster's network topology as a ring.

        The nodes communicate logically in a ring topology.
        Each node forwards the packet to the next node in the ring
        until the packet arrives at its desired destination.
        The ring is built incrementally as specified in the config file.
        The forwarding direction is always clockwise.

        Keyword Arguments:
            remove {boolean} -- Remove the configuration (default: {False})
        """

        for nodex in self.topology.nodes:
            for nodey in self.topology.nodes:
                if nodex.node_id == nodey.node_id:
                    continue
                nodex.add_forwarding(nodey, self.topology.nodes[(
                    nodex.node_id + 1) % (self.topology.num_nodes)])

        if not self.testing:
            self.topology.send_forwarding_tables(remove)

    def configure_star_topology(self, center, remove=False):
        """Configures the cluster's network topology as a star.

        The specified center node is configured as the star's center point
        and is connected to every other node in a single hop.
        All the other nodes have to first send their packets to the center node
        where they are forwarded to the destination.

        Arguments:
            center {integer} -- The center node's index.
            remove {boolean} -- Remove the configuration (default: {False})
        """

        center_node = self.topology.get_node(center)
        for nodex in self.topology.nodes:
            self.logger.debug("%s:", nodex.name)
            if nodex.node_id == center_node.node_id:
                self.logger.debug(
                    "Configuring %s as center of the star topology.", nodex.name)
                for nodey in self.topology.nodes:
                    if nodex.node_id == nodey.node_id:
                        continue
                    nodex.add_forwarding(nodey, nodey)
            else:
                for nodey in self.topology.nodes:
                    if nodex.node_id == nodey.node_id:
                        continue
                    nodex.add_forwarding(nodey, center_node)

        if not self.testing:
            self.topology.send_forwarding_tables(remove)

    def configure_tree_topology(self, root, degree=2, remove=False):
        """Configures the cluster's network topology as a tree.

        The tree consists of the specified root node and the nodes,
        which build the subtrees. The childrens are incrementally chosen,
        in other words, sequentially as specified in the config file.

        Arguments:
            root {integer} -- The tree's root node.

        Keyword Arguments:
            degree {integer} -- The maximum number of children (default: {2})
            remove {boolean} -- Remove the configuration (default: {False})
        """

        tree = Tree()
        root_node = self.topology.get_node(root)
        tree.create_node(root_node.name, root_node.node_id)
        parent_node = root
        for nodex in self.topology.nodes:
            if nodex.node_id == root_node.node_id:
                continue
            if len(tree.children(parent_node)) >= degree:
                if parent_node == root and root != 0:
                    parent_node = 0
                elif parent_node + 1 == root:
                    parent_node += 2
                else:
                    parent_node += 1
            tree.create_node(nodex.name, nodex.node_id, parent_node)

        self.logger.info("The following tree will be configured:")
        tree.show()

        for nodex in self.topology.nodes:
            self.logger.debug("%s:", nodex.name)
            subtree = tree.subtree(nodex.node_id)
            for nodey in self.topology.nodes:
                if nodex.node_id == nodey.node_id:
                    continue
                if subtree.contains(nodey.node_id):
                    children = tree.children(nodex.node_id)
                    for child in children:
                        if (child.identifier == nodey.node_id or
                                tree.is_ancestor(child.identifier, nodey.node_id)):
                            nodex.add_forwarding(
                                nodey, self.topology.get_node(child.identifier))
                            break
                elif tree.parent(nodex.node_id) != None:
                    nodex.add_forwarding(nodey, self.topology.get_node(
                        tree.parent(nodex.node_id).identifier))

        if not self.testing:
            self.topology.send_forwarding_tables(remove)

    def open_shells(self):
        """Starts system shells and establishes SSH to all nodes.
        This is a helper method, to automatically start SSH sessions.
        """

        cmd = ""
        if platform == "linux" or platform == "linux2":
            cmd = Commands.cmd_start_shell_lin
        elif platform == "darwin":
            cmd = Commands.cmd_start_shell_mac
        elif platform == "win32":
            cmd = Commands.cmd_start_shell_win

        if cmd is not "":
            for node in self.topology.nodes:
                if platform == "darwin":
                    p = subprocess.Popen(['osascript', '-'],
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         universal_newlines=True)
                    p.communicate(cmd
                                  .format(os.path.abspath(SSH.PRIVATE_KEY_FILE), node.address))
                else:
                    subprocess.Popen(cmd
                                     .format(os.path.abspath(SSH.PRIVATE_KEY_FILE),
                                             node.address), shell=True)

    def open_shell(self, id):
        """Starts system shell and establishes SSH to specified node.
        This is a helper method, to automatically start SSH sessions.
        """

        cmd = ""
        if platform == "linux" or platform == "linux2":
            cmd = Commands.cmd_start_shell_lin
        elif platform == "darwin":
            cmd = Commands.cmd_start_shell_mac
        elif platform == "win32":
            cmd = Commands.cmd_start_shell_win

        if cmd is not "":
            if platform == "darwin":
                    p = subprocess.Popen(['osascript', '-'],
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         universal_newlines=True)
                    _, _ = p.communicate(cmd
                                         .format(os.path.abspath(SSH.PRIVATE_KEY_FILE),
                                                 self.topology.get_node(id).address))
            else:
                subprocess.Popen(cmd
                                 .format(os.path.abspath(SSH.PRIVATE_KEY_FILE),
                                         self.topology.get_node(id).address), shell=True)

    def execute_command_on_all(self, cmd):
        """Executes the specified command on every node.
        
        Arguments:
            cmd {string} -- Command.
        """

        self.topology.send_command_to_all(cmd)

    def set_up_cluster_ssh(self):
        """Setups the ssh keys for cluster internal communication.
        """

        self.generate_ssh_keys_on_cluster()
        self.exchange_ssh_public_keys_on_cluster()

    def generate_ssh_keys_on_cluster(self):
        """Generates ssh rsa key pairs on all nodes on the cluster.
        """

        for node in self.topology.nodes:
            if not node.connection.check_cluster_key_generated():
                node.connection.generate_remote_ssh_key()
            
    def exchange_ssh_public_keys_on_cluster(self):
        """Exchanges public ssh keys on all cluster nodes.
        """

        for nodex in self.topology.nodes:
            public_key = nodex.connection.get_public_key_from_remote()
            for nodey in self.topology.nodes:
                if nodex.node_id == nodey.node_id:
                    continue
                nodey.connection.share_key_with_host(public_key)

class Node:
    """This class provides the functionality of a node.
    """

    def __init__(self, node_id, name, address):
        self.logger = logging.getLogger('app.netconflib.Node')
        self.node_id = node_id
        self.name = name
        self.address = address
        self.connection = None
        self.forwarding_table = {}
        self.hosts = []

    def add_forwarding(self, dest_node, next_node):
        """Adds a forwarding entry to the table.

        Arguments:
            dest_node {Node} -- The destination node.
            next_node {Node} -- The next node to forward to.
        """

        self.logger.debug("%s: Adding following entry to forwarding table. -host %s gw %s"
                          , self.name, dest_node.name, next_node.name)
        self.forwarding_table.update({dest_node: next_node})

    def add_host(self, node):
        """Adds the specified node to the node's hosts.

        Arguments:
            node {Node} -- The node to be added.
        """

        self.logger.debug("%s: Adding %s to hosts.", self.name, node.name)
        self.hosts.append(node)

    def send_forwarding_table(self, remove=False):
        """Sends and writes the forwarding entries of this node
        to the corresponding physical node on the cluster.

        Keyword Arguments:
            remove {boolean} -- Remove the configuration (default: {False})
        """

        act = "add"
        if remove:
            act = "del"

        self.logger.debug("%s:", self.name)
        for dest, next_node in self.forwarding_table.items():
            self.logger.debug(
                "sudo route %s -host %s gw %s", act, dest.name, next_node.name)
            self.connection.send_command(
                "sudo route {} -host {} gw {}".format(act, dest.name, next_node.name))

    def send_hosts(self):
        """Sends and writes the hosts on the node's hosts file.
        """

        for node in self.hosts:
            name = node.name
            addr = node.address
            if self.node_id == node.node_id:
                addr = "127.0.0.1"
            self.logger.debug("%s: echo '%s    %s' | sudo tee -a /etc/hosts", self.name, addr, name)
            self.connection.send_command(
                "echo '{}    {}' | sudo tee -a /etc/hosts".format(addr, name))

    def send_command(self, cmd, block=True):
        """Sends and executes the provided command on the node.
        
        Arguments:
            cmd {string} -- Command.
        """

        self.logger.debug("Executing following command on node %s: '%s'", self.name, cmd)
        self.connection.send_command(cmd, block)

    def create_ssh_connection(self, username, password):
        """Creates an SSH connection to this node.
        The node's address is used. No connection will be created
        if the address is unspecified.

        Arguments:
            username {string} -- SSH username
            password {string} -- SSH password
        """

        if self.address != "":
            self.connection = SSH(self.address, username, password)
        else:
            raise ValueError

    def clean_up(self):
        """Clears variables.
        """

        if self.connection != None:
            self.connection.client.close()
        self.forwarding_table.clear()
        self.hosts.clear()

    def get_all_gateways(self):
        """Return all gateway addresses of this node.

        Returns:
            list -- List of gateway addresses.
        """

        gws = []
        for node in self.forwarding_table.values():
            gws.append(node.address)
        return gws

class Topology:
    """This class holds the topology of the cluster.
    """

    def __init__(self, topology_type, num_nodes, username, password):
        self.logger = logging.getLogger('app.netconflib.Topology')
        self.topology_type = topology_type
        self.num_nodes = num_nodes
        self.username = username
        self.password = password
        self.nodes = []

    def add_nodes_from_list(self, nodes):
        """Adds new nodes to the topology out of a list of (name, address) tuples.

        Arguments:
            nodes {list} -- List of (name, address) tuples.
        """

        for i, node in enumerate(nodes):
            new_node = Node(i, node[0], node[1])
            self.nodes.append(new_node)

    def clean_up(self):
        """Clears the variables.
        """

        for node in self.nodes:
            node.clean_up()
        self.nodes.clear()

    def get_node(self, node_id):
        """Returns the node that matches the specified id.

        Arguments:
            node_id {integer} -- The node id.

        Returns:
            Node -- The node object.
        """

        for node in self.nodes:
            if node.node_id == node_id:
                return node

    def get_nodes_count(self):
        """Return an integer indicating the number of nodes.
        
        Returns:
            integer -- Node count.
        """

        return self.num_nodes

    def create_all_connections(self):
        """Creates connections for every available node in the topology.
        """

        self.logger.info("Establishing connection to all specified nodes...")
        try:
            for node in self.nodes:
                self.logger.debug(
                    "Creating new connection to %s, %s...", node.name, node.address)
                node.create_ssh_connection(self.username, self.password)
        except (ValueError, BadHostKeyException, AuthenticationException, SSHException) as ex:
            self.logger.error(ex)
            self.logger.error("connection failed with %s.", node.name)
        self.logger.info("Connections setup done.")

    def send_forwarding_tables(self, remove=False):
        """Calls every node object on the cluster to send their forwarding table.

        Keyword Arguments:
            remove {boolean} -- Remove the configuration (default: {False})
        """

        for node in self.nodes:
            node.send_forwarding_table(remove)

    def send_all_hosts(self):
        """Calls every node object on the cluster to send their host entries.
        """

        for node in self.nodes:
            node.send_hosts()

    def send_command_to_all(self, cmd):
        """Executes the provided command on every node in parallel.
        
        Arguments:
            cmd {string} -- Command.
        """

        for node in self.nodes:
            node.send_command(cmd, False)

class TopologyTypes:
    """Available topology types.
    """

    TOPOLOGY_RING = "ring"
    TOPOLOGY_STAR = "star"
    TOPOLOGY_TREE = "tree"
