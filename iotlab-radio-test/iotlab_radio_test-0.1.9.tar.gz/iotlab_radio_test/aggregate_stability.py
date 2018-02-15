# -*- coding:utf-8 -*-
from __future__ import print_function
import os

import numpy as np
from numpy import genfromtxt

from iotlab_radio_test.config import (get_parsed_dir,
                                      get_exp_dir)
from iotlab_radio_test.constants import PREFIX_CONN_GOOD, PREFIX_STAB_GOOD, FORMAT_STRING_TX


class StabilityLogParser(object):
    """ Load links matrix and find stable links accross experiments %s :
        we make a logical AND.

        good links: PDR≥90% on all frequencies
        unbalanced links: PDR≥90% on some frequencies, PDR<90% on others
        bad links: PDR<90% on all frequencies
    """

    def __init__(self, config, experiments_dir, output_dir, expid_list, name):
        self.config = config
        self.expid_list = expid_list
        self.name = name
        self.experiments_dir = experiments_dir
        self.output_dir = output_dir
        # Put data into a 2D np array
        max1 = (max(self.config.node_list) + 1, max(self.config.node_list) + 1)
        self.good_links = np.zeros(max1, dtype=np.bool)

    def parse_file(self, txpower, expid_A, expid_B=None):
        """ Load boolean 2D np array and make a logical AND.

            [[0,0,0,0,1,0,0,0,1, ... ,0,0,1,0,1,0,1,0,0,0,0,0,0]
             [0,0,0,0,1,0,0,0,1, ... ,0,0,1,0,1,0,1,0,0,0,0,0,0]
             ...
             [0,0,0,0,1,0,0,0,1, ... ,0,0,1,0,1,0,1,0,0,0,0,0,0]]

            Put stability results in 2D boolean np array
        """
        self.txpower = txpower
        # Load good links
        good_links_A = self.load_good_links(txpower, expid_A)
        if expid_B != None:
            print("compare %s with %s" % (expid_A, expid_B))
            good_links_B = self.load_good_links(txpower, expid_B)
            np.logical_and(good_links_A, good_links_B, self.good_links)
            self.print_stats()
        else:
            print("compare %s with previous results" % expid_A)
            np.logical_and(good_links_A, self.good_links, self.good_links)
            self.print_stats()

    def load_good_links(self, txpower, experiment_id):
        parsed_dir = get_parsed_dir(get_exp_dir(experiment_id, self.experiments_dir))
        input_conn_filename = FORMAT_STRING_TX.format(PREFIX_CONN_GOOD, txpower, "csv")
        input_conn_full_path = os.path.join(parsed_dir, input_conn_filename)
        return np.array(genfromtxt(input_conn_full_path, delimiter=',', dtype="int"))

    def print_stats(self):
        """ Print links stats
        """
        good = 0

        # Count bidirectional links
        for node_src in self.config.node_list:
            for node_dst in self.config.node_list:
                if node_src < node_dst:
                    # good/good uni => good bi
                    if self.good_links[node_src, node_dst]\
                            and self.good_links[node_dst, node_src]:
                        good = good + 1

        print("Good links uni %d bi %d" % (np.count_nonzero(self.good_links), good))

    def save_results(self):
        """ Save array
        """
        # good links
        output_stability_filename = FORMAT_STRING_TX.format(PREFIX_STAB_GOOD, self.txpower, "csv")
        output_stability_full_path = os.path.join(self.output_dir, output_stability_filename)
        save_csv(output_stability_full_path)
        np.savetxt(output_stability_full_path, self.good_links, delimiter=",", fmt="%d")
