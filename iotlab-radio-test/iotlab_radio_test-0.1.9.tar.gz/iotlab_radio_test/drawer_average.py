# -*- coding:utf-8 -*-


import numpy as np
from matplotlib.mlab import griddata


class DrawerAverage(object):
    """
    Drawer Average class,

    Load average data from a given channel/file and draw them into a wireframe.

    X,Y are nodes coordinates,
    Z are metric values.
    """

    #pylint: disable=too-many-instance-attributes

    def __init__(self, config, input_average_full_path, axis,
                 nodes, metric, channel, colors_channel):
        self.config = config
        self.input_average_full_path = input_average_full_path
        self.axis = axis
        self.nodes = nodes
        self.metric = metric
        self.channel = channel
        self.colors_channel = colors_channel

    def process_data(self):
        """ Main process function
        """
        self.load_data()
        self.draw_wireframe()

    def load_data(self):
        """ Load data from average file
        """
        # Load data from average file
        self.data = np.genfromtxt(self.input_average_full_path, delimiter=',', dtype="int")

        # Update data to nodes array
        for row in self.data:
            self.nodes[row[0]].pdr = row[3]
            self.nodes[row[0]].rssi = row[4]
            self.nodes[row[0]].lqi = row[5]

    def draw_wireframe(self):
        """ Draw nodes data
        """
        # Init all np array
        fid, fx, fy, fz = [], [], [], []

        # Iterate to all nodes data
        for cur_node in self.nodes.itervalues():
            if cur_node.mobile != 1:
                fx.append(float(cur_node.x))
                fy.append(float(cur_node.y))
                if self.metric == "rssi":
                    fz.append(float(cur_node.rssi))
                elif self.metric == "lqi":
                    fz.append(float(cur_node.lqi))
                elif self.metric == "pdr":
                    fz.append(float(cur_node.pdr))
                else:
                    raise ValueError('metric can only be rssi, lqi or pdr')
                fid.append(str(cur_node.node_id))

        # Plot wireframe
        xi = np.linspace(min(fx), max(fx))
        yi = np.linspace(min(fy), max(fy))
        X, Y = np.meshgrid(xi, yi)
        Z = griddata(fx, fy, fz, xi, yi, interp='linear')
        color = self.colors_channel[
            self.config.radio.channel_list.index(self.channel)]
        self.axis.plot_wireframe(X, Y, Z,
                                 rstride=5,
                                 cstride=5,
                                 color=color,
                                 label="ch " + str(self.channel))

        # Plot also nodes in same color in order to be more readable
        color = self.colors_channel[
            self.config.radio.channel_list.index(self.channel)]
        self.axis.plot(fx, fy, fz, ls="None", marker=".", zorder=90, color=color)

        font_size = self.config.draw.font_size
        # Plot labels
        self.axis.set_xlabel("Width (m)", size=font_size)
        self.axis.set_ylabel("Length (m)", size=font_size)
        if self.metric == "rssi":
            self.axis.set_zlabel("RSSI (dBm)", size=font_size, rotation=90)
        elif self.metric == "lqi":
            self.axis.set_zlabel("LQI", size=font_size, rotation=90)
        else:
            self.axis.set_zlabel("PDR (%)", size=font_size, rotation=90)
            self.axis.set_zlim(75, 100)
