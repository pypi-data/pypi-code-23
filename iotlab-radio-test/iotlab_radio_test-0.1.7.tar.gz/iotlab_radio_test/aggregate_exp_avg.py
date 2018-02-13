from __future__ import print_function
import os

import numpy as np
from numpy import genfromtxt

from iotlab_radio_test import topology as topology
from iotlab_radio_test.config import get_parsed_dir, get_exp_dir
from iotlab_radio_test.constants import (PREFIX_RAW, PREFIX_MERGE,
                                         PREFIX_AVERAGE, FORMAT_STRING_CH_TX)


def unique_rows(array):
    array = np.ascontiguousarray(array)
    unique_a = np.unique(array.view([('', array.dtype)] * array.shape[1]))
    return unique_a.view(array.dtype).reshape((unique_a.shape[0], array.shape[1]))


class AvgLogParser(object):
    """ Average of multiple experiments
    """

    def __init__(self, config, api, experiments_dir, avg_dir, expid_list, name):
        self.config = config
        self.expid_list = expid_list
        self.experiments_dir = experiments_dir
        self.name = name
        self.input_prefix = PREFIX_RAW
        self.output_merge_prefix = PREFIX_MERGE
        self.output_average_prefix = PREFIX_AVERAGE
        self.input_average_prefix = PREFIX_AVERAGE
        self.avg_dir = avg_dir

        # Load first clusters and then nodes topology
        self.clusters8, self.clusters16 = topology.load_cluster_topology(config)
        self.nodes = topology.load_node_topology(config, api, self.clusters8)

    def parse_file(self, channel, txpower):
        """ Parse line by line
        """
        # New result dict
        results_average = np.empty((0, 6), dtype=int)
        pdr_avg = 0
        rssi_avg = 0
        lqi_avg = 0

        # reinit previous average
        for cur_node in self.nodes.itervalues():
            cur_node.pdr = 0
            cur_node.rssi = 0
            cur_node.lqi = 0

        input_average_filename = FORMAT_STRING_CH_TX.format(self.input_average_prefix, channel, txpower, 'csv')
        # Load per experiment average data
        for expid in self.expid_list:
            parsed_dir = get_parsed_dir(get_exp_dir(expid, self.experiments_dir))
            input_average_full_path = os.path.join(parsed_dir, input_average_filename)
            print(input_average_full_path)
            data = genfromtxt(input_average_full_path, delimiter=',', dtype="int")

            #
            # [[  2  30  31  85 -81 252]
            # [  4  29  31  83 -77 254]
            # [  6  30  31  85 -78 253]
            #

            print(data)
            for row in data:
                self.nodes[row[0]].pdr = self.nodes[row[0]].pdr + row[3]
                self.nodes[row[0]].rssi = self.nodes[row[0]].rssi + row[4]
                self.nodes[row[0]].lqi = self.nodes[row[0]].lqi + row[5]

        for cur_node in self.nodes.itervalues():
            pdr_avg = cur_node.pdr / len(self.expid_list)
            rssi_avg = cur_node.rssi / len(self.expid_list)
            lqi_avg = cur_node.lqi / len(self.expid_list)
            np_line = np.array([[int(cur_node.node_id), 0, 0, int(pdr_avg), int(rssi_avg), int(lqi_avg)]])
            results_average = np.append(results_average, np_line, axis=0)

        # Remove duplicate row if exists and save to file
        output_avg_full_path = os.path.join(self.avg_dir, input_average_filename)
        np.savetxt(output_avg_full_path, unique_rows(results_average), delimiter=",", fmt="%d")
