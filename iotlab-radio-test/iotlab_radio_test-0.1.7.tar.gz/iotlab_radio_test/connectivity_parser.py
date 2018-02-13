# -*- coding: utf-8 -*-
import logging
import os

import numpy as np
from numpy import genfromtxt

from iotlab_radio_test.constants import (PREFIX_MERGE, PREFIX_CONN_GOOD,
                                         PREFIX_CONN_UNBALANCED, PREFIX_CONN_BAD,
                                         FORMAT_STRING_CH_TX, FORMAT_STRING_TX)


class ConnectivityLogParser(object):
    """ Parse merge log outputs in order to get links stability :

        good links: PDR≥90% on all frequencies
        unbalanced links: PDR≥90% on some frequencies, PDR<90% on others
        bad links: PDR<90% on all frequencies
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, config, parsed_dir, txpower):
        self.config = config
        self.parsed_dir = parsed_dir
        # Load first clusters and then nodes topology
        # Put data into a 2D np array
        max1 = (max(self.config.node_list) + 1, max(self.config.node_list) + 1)
        self.good_links_matrix = np.zeros(max1, dtype=np.int)
        self.good_links = set()
        max2 = (max(self.config.node_list) + 1, max(self.config.node_list) + 1)
        self.unbalanced_links_matrix = np.zeros(max2, dtype=np.int)
        self.unbalanced_links = set()
        max3 = (max(self.config.node_list) + 1, max(self.config.node_list) + 1)
        self.bad_links_matrix = np.zeros(max3, dtype=np.int)
        self.bad_links = set()

        self.links = {}

        self.txpower = txpower

    def get_data(self, channel):
        # Merge file fullpath
        input_merge_filename = FORMAT_STRING_CH_TX.format(PREFIX_MERGE, channel, self.txpower, 'csv')
        # print "parsing %s file" % input_merge_filename
        input_merge_full_path = os.path.join(self.parsed_dir, input_merge_filename)
        # Load file
        data = genfromtxt(input_merge_full_path, delimiter=',', dtype="int")
        return data

    def parse_file(self, channel):
        """ Parse line by line data file

             [[  2  30  31  85 -81 252]
             [  4  29  31  83 -77 254]
             [  6  30  31  85 -78 253]

            Put connectivity results in three 2D np array
        """

        # Parse line by line
        for row in self.get_data(channel):
            tx_node = row[0]
            rx_node = row[1]
            element = (tx_node, rx_node)
            pdr = row[3]

            self.links[element] = pdr

            # Run sort algorithm, first check if not the same node, ie rx_node=0
            if int(rx_node) == 0:
                continue

            # PDR above 90%
            if pdr >= 90:
                # Check if previously unbalanced or bad
                if self.unbalanced_links_matrix[element] == 0 \
                        and self.bad_links_matrix[element] == 0:
                    # If not, we are still a good link
                    self.good_links_matrix[element] = 1
                    self.good_links.add(element)
                else:
                    # otherwise we are unbalanced
                    self.good_links_matrix[element] = 0
                    self.bad_links_matrix[element] = 0
                    self.unbalanced_links_matrix[element] = 1

                    if element in self.good_links:
                        self.good_links.remove(element)
                    if element in self.bad_links:
                        self.bad_links.remove(element)
                    self.unbalanced_links.add(element)
            # PDR under 90%
            else:
                # Check if previously good or unbalanced
                if self.good_links_matrix[element] == 0 \
                        and self.unbalanced_links_matrix[element] == 0:
                    # If not, we are still a bad link
                    # print "BAD (%s,%s)" % (tx_node,rx_node)
                    self.bad_links_matrix[element] = 1
                    self.bad_links.add(element)
                else:
                    # otherwise we are unbalanced
                    self.good_links_matrix[element] = 0
                    self.bad_links_matrix[element] = 0
                    self.unbalanced_links_matrix[element] = 1

                    if element in self.good_links:
                        self.good_links.remove(element)
                    if element in self.bad_links:
                        self.bad_links.remove(element)
                    self.unbalanced_links.add(element)

    def print_stats(self):
        """ Print links stats
        """
        good = 0
        unbalanced = 0
        bad = 0

        # Count bidirectional links
        for node_src in self.config.node_list:
            for node_dst in self.config.node_list:
                if node_src >= node_dst:
                    continue
                # good/good link good
                # good/unbalanced => unbalanced
                # good/bad => unbalanced
                if self.good_links_matrix[node_src][node_dst] == 1 \
                        and self.good_links_matrix[node_dst][node_src] == 1:
                    good = good + 1
                elif self.good_links_matrix[node_src][node_dst] == 1 \
                        and self.unbalanced_links_matrix[node_dst][node_src] == 1:
                    unbalanced = unbalanced + 1
                elif self.good_links_matrix[node_src][node_dst] == 1 \
                        and self.bad_links_matrix[node_dst][node_src] == 1:
                    unbalanced = unbalanced + 1
                # unbalanced/unbalanced link or
                # unbalanced/good link or
                # unbalanced/bad link
                if self.unbalanced_links_matrix[node_src][node_dst] == 1 \
                        and self.unbalanced_links_matrix[node_dst][node_src] == 1:
                    unbalanced = unbalanced + 1
                elif self.unbalanced_links_matrix[node_src][node_dst] == 1 \
                        and self.good_links_matrix[node_dst][node_src] == 1:
                    unbalanced = unbalanced + 1
                elif self.unbalanced_links_matrix[node_src][node_dst] == 1 \
                        and self.bad_links_matrix[node_dst][node_src] == 1:
                    unbalanced = unbalanced + 1
                # bad/bad link => bad
                # bad/unbalanced => unbalanced
                # bad/good => unbalanced
                if self.bad_links_matrix[node_src][node_dst] == 1 \
                        and self.bad_links_matrix[node_dst][node_src] == 1:
                    bad = bad + 1
                elif self.bad_links_matrix[node_src][node_dst] == 1 \
                        and self.unbalanced_links_matrix[node_dst][node_src] == 1:
                    unbalanced = unbalanced + 1
                elif self.bad_links_matrix[node_src][node_dst] == 1 \
                        and self.good_links_matrix[node_dst][node_src] == 1:
                    unbalanced = unbalanced + 1

        logging.info("TX Power %s ", self.txpower)
        logging.info("Good links uni %d bi %d",
                     np.count_nonzero(self.good_links_matrix), good)
        logging.info("Unbalanced links uni %d bi %d",
                     np.count_nonzero(self.unbalanced_links_matrix), unbalanced)
        logging.info("Bad links uni %d bi %d",
                     np.count_nonzero(self.bad_links_matrix), bad)

    def save_csv(self, prefix, data):
        output_connectivity_filename = FORMAT_STRING_TX.format(prefix, self.txpower, "csv")
        output_connectivity_full_path = os.path.join(self.parsed_dir, output_connectivity_filename)
        np.savetxt(output_connectivity_full_path, data, delimiter=",", fmt="%d")

    def save_results(self):
        """ Save array
        """
        # good links
        self.save_csv(PREFIX_CONN_GOOD, self.good_links_matrix)
        # unbalanced links
        self.save_csv(PREFIX_CONN_UNBALANCED, self.unbalanced_links_matrix)
        # bad links
        self.save_csv(PREFIX_CONN_BAD, self.bad_links_matrix)
