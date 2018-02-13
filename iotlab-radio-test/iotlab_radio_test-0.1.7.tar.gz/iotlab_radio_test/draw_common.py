# -*- coding:utf-8 -*-
from collections import namedtuple

import numpy as np


def draw_wifi_ap_coordinates(config, axis):
    """ Draw Wi-Fi coordinates
    """
    # put markers to the floor
    z_floor = axis.get_zlim3d()[0]

    # Plots Wi-Fi AP with red diamond markers
    for i, wifi_ap in enumerate(config.draw.wifi):
        # Print legend label for the first AP
        if i == 0:
            axis.plot([wifi_ap.X], [wifi_ap.Y], [z_floor],
                      ls="None", marker="D", markersize=12,
                      zorder=90, color='r', label="Wi-Fi")
        else:
            axis.plot([wifi_ap.X], [wifi_ap.Y[i]], [z_floor],
                      ls="None", marker="D", markersize=12,
                      zorder=90, color='r')

    # Show label inside figure
    for wifi_ap in config.draw.wifi:
        axis.text(wifi_ap.X - 1, wifi_ap.Y + 0.2,
                  z_floor, "%s" % wifi_ap.Name,
                  size=14, color='r', zorder=-100)


def draw_robot_coordinates(config, axis):
    """ Draw Robot coordinates
    """
    # put markers to the floor
    z_floor = axis.get_zlim3d()[0]

    # Plots Robot
    for i, robot in enumerate(config.draw.robots):
        # Print legend label for the first robot
        if i == 0:
            axis.plot([robot.X], [robot.Y], [z_floor],
                      ls="None", marker="s", markersize=12,
                      zorder=90, color='b', label="Turtlebot2")
        else:
            axis.plot([robot.X], [robot.Y], [z_floor],
                      ls="None", marker="s", markersize=12,
                      zorder=90, color='b')


def draw_nodes_coordinates(config, axis, nodes, default_height=False):
    """ Draw nodes coordinates
    """
    # Init all variables
    nodes_x, nodes_y, nodes_z, nodes_id = [], [], [], []
    font_size = config.draw.font_size

    # Plots nodes to the floor of the graph
    if default_height is False:
        # put markers to the floor
        z_floor = axis.get_zlim3d()[0]
        y_pan = axis.get_ylim3d()[1] - axis.get_ylim3d()[0]
        z_pan = axis.get_zlim3d()[1] - axis.get_zlim3d()[0]
        z_offset = (0.2 * z_pan) / y_pan

        for cur_node in nodes.itervalues():
            nodes_x.append(float(cur_node.x))
            nodes_y.append(float(cur_node.y))
            nodes_z.append(float(z_floor))
            nodes_id.append(str(cur_node.node_id))
        for i in np.arange(0, len(nodes_x)):
            axis.plot([nodes_x[i]], [nodes_y[i]], [z_floor],
                      ls="None", marker=".", zorder=90, color='black')
        for i in np.arange(0, len(nodes_x)):
            axis.text(nodes_x[i], nodes_y[i] + 0.2, z_floor + z_offset, "%s" % nodes_id[i],
                      size=font_size, color='k', zorder=100)
    # Plots nodes to their real height
    else:
        for cur_node in nodes.itervalues():
            nodes_x.append(float(cur_node.x))
            nodes_y.append(float(cur_node.y))
            nodes_z.append(float(cur_node.z))
            nodes_id.append(str(cur_node.node_id))
        for i in np.arange(0, len(nodes_x)):
            axis.plot([nodes_x[i]], [nodes_y[i]], [nodes_z[i]], ls="None", marker=".",
                      zorder=90, color='black')
        for i in np.arange(0, len(nodes_x)):
            axis.text(nodes_x[i], nodes_y[i] + 0.5, nodes_z[i] + 0.01, "%s" % nodes_id[i],
                      size=font_size, color='k', zorder=100)


DrawArgs = namedtuple('DrawArgs', ['metric', 'stability', 'save', 'nodes', 'wifi', 'robot'])
