# -*- coding:utf-8 -*-
from __future__ import print_function
import os

import numpy as np
from numpy import genfromtxt

import iotlab_radio_test.draw_common as dc
import iotlab_radio_test.topology as topology
from iotlab_radio_test.config import (get_exp_dir,
                                      get_parsed_dir)
from iotlab_radio_test.constants import (PREFIX_CONN_GOOD, PREFIX_CONN_UNBALANCED,
                                         PREFIX_CONN_BAD, PREFIX_STAB_GOOD,
                                         FORMAT_STRING_TX)


class DrawerConnectivity(object):
    """
    Drawer Connectivity class,
    load connectivity data and draw them.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, config, parsed_dir, axis,
                 nodes, metric, channel,
                 txpower, colors_channel,
                 clusters, show_stability):
        self.config = config
        self.parsed_dir = parsed_dir
        self.show_stability = show_stability
        if show_stability:
            self.parsed_dir_stability_results = get_parsed_dir(get_exp_dir(show_stability))
        self.axis = axis
        self.nodes = nodes
        self.metric = metric
        self.channel = channel
        self.txpower = txpower
        self.colors_channel = colors_channel
        self.clusters = clusters
        self.clusters_centroids = topology.clusters_centroids(self.clusters, self.nodes)
        print(self.show_stability)

    def process_data(self):
        """ Main process function
        """
        self.load_data()
        self.draw_connectivity()

    def load_data(self):
        """ Load data from merge file.
            Try to get bi-directionnal metric links into a 2D np array
        """
        # good links
        self.good_links = self.links_from_file(PREFIX_CONN_GOOD)
        # good links stables
        if self.show_stability:
            self.good_links_stable = self.links_from_file(PREFIX_STAB_GOOD)
        # unbalanced links
        self.unbalanced_links = self.links_from_file(PREFIX_CONN_UNBALANCED)
        # bad links
        self.bad_links = self.links_from_file(PREFIX_CONN_BAD)

    def links_from_file(self, prefix):
        filename = FORMAT_STRING_TX.format(prefix, self.txpower, "csv")
        full_path = os.path.join(self.parsed_dir, filename)
        print("open file %s" + full_path)
        return genfromtxt(full_path, delimiter=',', dtype=np.bool)

    def draw_connectivity(self):
        """ Draw nodes connectivity.
            Draw links by category (good,unbalanced,bad)
        """
        # Plot good links
        for node_src in self.config.node_list:
            for node_dst in self.config.node_list:
                if node_src < node_dst:
                    # do not plot stable links
                    if self.show_stability:
                        if self.good_links_stable[node_src][node_dst] \
                                and self.good_links_stable[node_dst][node_src]:
                            continue
                    # but only good/good link
                    elif self.good_links[node_src][node_dst] \
                            and self.good_links[node_dst][node_src]:
                        self.draw_node_link(node_src, node_dst, 'chartreuse')

        # Plot stab links accross experiments
        if self.show_stability:
            for node_src in self.config.node_list:
                for node_dst in self.config.node_list:
                    # good/good link stable
                    if node_src < node_dst \
                            and self.good_links_stable[node_src][node_dst] \
                            and self.good_links_stable[node_dst][node_src]:
                        self.draw_node_link(node_src, node_dst, 'r', linestyle='--')
        # Plot nodes
        dc.draw_nodes_coordinates(self.config, self.axis, self.nodes, default_height=True)
        # Set labels
        self.axis.set_xlabel("Width (m)")
        self.axis.set_ylabel("Length (m)")
        self.axis.set_zlabel("Heigth (m)", rotation=90)

    def draw_node_link(self, src, dst, color, linestyle=None):
        """ Draw link between src and dst nodes
        """
        src_x = float(self.nodes[src].x)
        dst_x = float(self.nodes[dst].x)
        src_y = float(self.nodes[src].y)
        dst_y = float(self.nodes[dst].y)
        src_z = float(self.nodes[src].z)
        dst_z = float(self.nodes[dst].z)
        src_id = self.nodes[src].node_id
        dst_id = self.nodes[dst].node_id
        print(src_id, dst_id)

        # Plot Link
        if linestyle != None:
            self.axis.plot([src_x, dst_x], [src_y, dst_y], [src_z, dst_z],
                           color=color,
                           linestyle=linestyle)
        else:
            self.axis.plot([src_x, dst_x], [src_y, dst_y], [src_z, dst_z],
                           color=color)

    def draw_clusters_connectivity(self):
        """ Draw clusters connectivity.
            Draw links that are between pdr_min and pdr_max
        """
        # Plot Links
        for node_src in self.config.node_list:
            for node_dst in self.config.node_list:
                if node_src != node_dst:
                    self.draw_cluster_link(node_src, node_dst)

        # Set labels
        self.axis.set_xlabel("Width (m)")
        self.axis.set_ylabel("Length (m)")
        self.axis.set_zlabel("Height (m)", rotation=90)

    def draw_cluster_link(self, src, dst):
        """ Draw link between src and dst nodes
        """
        src_cs_id = self.nodes[src].cluster_id
        dst_cs_id = self.nodes[dst].cluster_id

        # do not draw links inside our cluster
        if src_cs_id == dst_cs_id:
            return

        src_x = self.clusters_centroids[src_cs_id][0]
        dst_x = self.clusters_centroids[dst_cs_id][0]
        src_y = self.clusters_centroids[src_cs_id][1]
        dst_y = self.clusters_centroids[dst_cs_id][1]
        # src_z = float(self.nodes[str(src)].z)
        # dst_z = float(self.nodes[str(dst)].z)
        src_z = float(self.channel)
        dst_z = float(self.channel)
        color = self.colors_channel[
            self.config.radio.channel_list.index(self.channel)]
        self.axis.plot([src_x, dst_x], [src_y, dst_y], [src_z, dst_z],
                       color=color)

        color = self.colors_channel[
            self.config.radio.channel_list.index(self.channel)]
        self.axis.plot([src_x], [src_y], [src_z],
                       ls="None",
                       marker=".",
                       zorder=90,
                       color=color)
        color = self.colors_channel[
            self.config.radio.channel_list.index(self.channel)]
        self.axis.plot([dst_x], [dst_y], [dst_z],
                       ls="None",
                       marker=".",
                       zorder=90,
                       color=color)
