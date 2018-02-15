import os

import numpy as np
from matplotlib import cm, pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from iotlab_radio_test import topology as topology, draw_common as dc
from iotlab_radio_test.drawer_average import DrawerAverage
from iotlab_radio_test.drawer_connectivity import DrawerConnectivity
from iotlab_radio_test.constants import PREFIX_AVERAGE, PREFIX_IMAGE, FORMAT_STRING, FORMAT_STRING_CH_TX, METRIC_CHOICES


class ImageGenerator(object):

    # pylint: disable=too-many-instance-attributes

    def __init__(self, config, api, image_dir, parsed_dir):
        self.config = config
        self.parsed_dir = parsed_dir
        self.image_dir = image_dir
        # Load first clusters and then nodes topology
        self.clusters8, self.clusters16 = topology.load_cluster_topology(config)
        self.nodes = topology.load_node_topology(config, api, self.clusters8)
        # Init color channels panel
        self.colors_channel = cm.rainbow(np.linspace(0, 1, len(config.radio.channel_list))) # pylint: disable=no-member
        # Init 3D graph
        self.avg_ax = self.init_3d_graph()

    @staticmethod
    def init_3d_graph():
        """ init 3D graph
        """
        fig = plt.figure()
        axes = Axes3D(fig)
        return axes

    def parse_file(self, channel, txpower, metric, stability):
        """ Parse data file
        """
        # Average file fullpath
        input_filename = FORMAT_STRING_CH_TX.format(PREFIX_AVERAGE, channel, txpower, 'csv')
        input_full_path = os.path.join(self.parsed_dir, input_filename)


        # Load raw merge data for drawing nodes connectivity
        if metric not in METRIC_CHOICES:
            raise ValueError('metric can only be in %s' % (','.join(METRIC_CHOICES)))
        if metric == "connectivity":
            drawer_conn = DrawerConnectivity(self.config, self.parsed_dir,
                                             self.avg_ax, self.nodes, metric,
                                             channel, txpower, self.colors_channel,
                                             self.clusters8, stability)
            drawer_conn.process_data()
        # Load average data for drawing pdr, rssi, lqi
        else:
            drawer_avg = DrawerAverage(self.config, input_full_path,
                                       self.avg_ax, self.nodes, metric,
                                       channel, self.colors_channel)
            drawer_avg.process_data()

    def draw_image(self, nodes, wifi, robot):
        """ Draw image
        """
        # Draw nodes position from current testbed topology
        if nodes:
            dc.draw_nodes_coordinates(self.config, self.avg_ax, self.nodes)
        # Optional informations
        if wifi:
            dc.draw_wifi_ap_coordinates(self.config, self.avg_ax)
        if robot:
            dc.draw_robot_coordinates(self.config, self.avg_ax)
        # Set camera orientation
        self.avg_ax.view_init(elev=self.config.draw.elev, azim=self.config.draw.azim)
        # Set legend
        self.avg_ax.legend(loc="upper left", numpoints=1, prop={'size':12})

    def save_image(self, save):
        """ Show or save figure into file
        """
        plt.show()
        if save:
            # Output image file
            output_image_filename = FORMAT_STRING.format(PREFIX_IMAGE, 'pdf')
            output_image_full_path = os.path.join(self.image_dir, output_image_filename)
            plt.savefig(output_image_full_path)
