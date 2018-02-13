# -*- coding:utf-8 -*-

""" Load topology and cluster resources files """

import json

from iotlabcli import Api
from iotlabcli.auth import get_user_credentials
from iotlabcli.experiment import info_experiment

from iotlab_radio_test.constants import TOPOLOGY_CLUSTER
from iotlab_radio_test.nodes import Node


def load_node_topology(config, api, clusters=None):
    """ Load topology from file """
    nodes = {}
    topology = info_experiment(api)
    for exp_node in config.node_list:
        for item in topology['items']:
            node_id = int(item["network_address"].split(".")[0].split("-")[-1])
            node_site = item["site"]
            node_archi = item["archi"].split(":")[0]
            if node_id == exp_node and node_site == config.site and node_archi == config.archi:

                def try_float(value, default=0):
                    try:
                        return float(value)
                    except ValueError:
                        return default

                node = Node(archi=item["archi"],
                            node_id=node_id,
                            network_address=item["network_address"],
                            x=try_float(item["x"]),
                            y=try_float(item["y"]),
                            z=try_float(item["z"]),
                            mobile=True if item["mobile"]=="1" else False)
                if clusters is not None:
                    for cluster_id, cluster in enumerate(clusters):
                        # print cs_id, cs
                        if node_id in cluster:
                            # print "add %s to cluster #%s : %s" % (node_id, cs_id, cs)
                            node.cluster_id = int(cluster_id)
                            break
                nodes[node_id] = node
                break
    return nodes


def load_cluster_topology(config):
    """ Load cluster topology from file """
    clusters_topology_file = TOPOLOGY_CLUSTER % config.site
    try:
        clusters = json.loads(open(clusters_topology_file).read())
    except:
        return [], []

    clusters8, clusters16 = [], []

    for cluster_8 in clusters['8']:
        newc8 = []
        for node_id in cluster_8:
            if node_id in config.node_list:
                newc8.append(node_id)
        if newc8:
            clusters8.append(sorted(newc8))

    for cluster_16 in clusters['16']:
        newc16 = []
        for c8_id in cluster_16:
            for node_id in clusters['8'][c8_id - 1]:
                if node_id in config.node_list:
                    newc16.append(node_id)
        if newc16:
            clusters16.append(sorted(newc16))

    return clusters8, clusters16


def clusters_centroids(clusters, nodes):
    """ return centroids for a groups of clusters """
    _clusters_centroids = []
    for cluster in clusters:
        centroid = compute_cluster_centroid(cluster, nodes)
        _clusters_centroids.append(centroid)
    return _clusters_centroids


def compute_cluster_centroid(cluster, nodes):
    """ Compute centroid of a cluster of nodes
    """
    # Init all variables
    x_positions, y_positions, z_positions = [], [], []
    # Add all coordinates into np array
    for node_id in cluster:
        x_positions.append(float(nodes[str(node_id)].x))
        y_positions.append(float(nodes[str(node_id)].y))
        z_positions.append(float(nodes[str(node_id)].z))
    # perform centroid
    _len = len(x_positions)
    centroid_x = sum(x_positions) / _len
    centroid_y = sum(y_positions) / _len
    centroid_z = sum(z_positions) / _len
    return [centroid_x, centroid_y, centroid_z]
