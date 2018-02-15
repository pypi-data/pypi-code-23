import logging
import os

import numpy as np
from namedlist import namedlist

from iotlab_radio_test.constants import (PREFIX_RAW, PREFIX_MERGE,
                                         PREFIX_AVERAGE, FORMAT_STRING_CH_TX)
from iotlab_radio_test.utils import save_csv


class RowLogFileParser(object):
    """
    Parses files with raw log
    """

    def __init__(self, raw_dir, parsed_dir):
        self.raw_dir = raw_dir
        self.parsed_dir = parsed_dir
        if not os.path.exists(self.parsed_dir):
            os.makedirs(self.parsed_dir)

    def parse_file(self, config, channel, txpower):
        # radio-ch11-txm17.log
        input_filename = FORMAT_STRING_CH_TX.format(PREFIX_RAW, channel, txpower, 'log')
        input_full_path = os.path.join(self.raw_dir, input_filename)
        logging.debug("writing file to %s ", input_filename)
        with open(input_full_path, 'r') as input_file:
            unique_results = parse_unique_results(input_file)

        results_average = parse_results_average(config, unique_results)

        self.save_parse_output(PREFIX_MERGE, channel, txpower, unique_results)
        self.save_parse_output(PREFIX_AVERAGE, channel, txpower, results_average)

    def save_parse_output(self, prefix, channel, txpower, results):
        output_filename = FORMAT_STRING_CH_TX.format(prefix, channel,
                                                     txpower, 'csv')
        output_full_path = os.path.join(self.parsed_dir, output_filename)
        save_csv(output_full_path, results)


#
# collection of functions that parse raw log strings
#


def parse_results_average(config, unique_results):
    data = namedlist('data',
                     ['msg_count', 'packet_sum', 'packet_avg', 'rssi_sum',
                      'rssi_avg', 'lqi_sum', 'lqi_avg', 'pdr', 'line'],
                     default=0)

    datas = {}
    for node_id in config.node_list:
        datas[node_id] = data()

    for row in unique_results:

        node_id = row[0]

        # ignore results with missing tx_node,
        if row[1] != 0:
            # print row
            datas[node_id].msg_count = datas[node_id].msg_count + 1
            datas[node_id].packet_sum = datas[node_id].packet_sum + row[3]
            datas[node_id].rssi_sum = datas[node_id].rssi_sum + row[4]
            datas[node_id].lqi_sum = datas[node_id].lqi_sum + row[5]

            if datas[node_id].msg_count != 0:
                datas[node_id].rssi_avg = datas[node_id].rssi_sum / datas[node_id].msg_count
                datas[node_id].lqi_avg = datas[node_id].lqi_sum / datas[node_id].msg_count
                # Consider as 100% packet loss (or not ?)
                # but do not count it in RSSI and LQI average
                datas[node_id].pdr = datas[node_id].packet_sum / len(config.node_list)
                # pdr = packet_sum / msg_count
            # print node_id, msg_count, len(config.NODE_LIST), pdr, rssi_avg, lqi_avg
            return_value = [int(node_id),
                            int(datas[node_id].msg_count),
                            int(len(config.node_list)),
                            int(datas[node_id].pdr),
                            int(datas[node_id].rssi_avg),
                            int(datas[node_id].lqi_avg)]
            datas[node_id].line = np.array(
                [return_value], dtype=int)
            pass

    results_average = np.concatenate([datas[node_id].line for node_id in config.node_list])

    return results_average


def parse_unique_results(lines):
    # New result dict
    results = np.empty((0, 6), dtype=int)
    for line in lines:
        np_line = parse_line(line)
        if np_line is not None:
            results = np.append(results, np_line, axis=0)

    # Remove duplicate row if exists and save to file
    return unique_rows(results)


def unique_rows(array):
    array = np.ascontiguousarray(array)
    unique_a = np.unique(array.view([('', array.dtype)] * array.shape[1]))
    return unique_a.view(array.dtype).reshape((unique_a.shape[0], array.shape[1]))


def parse_line(line):
    splitted_line = line.split(";")
    node_id = splitted_line[1].split("-")[1]
    payload = splitted_line[2]

    # ignore ACK receive messages
    if 'ACK' not in payload:
        try:
            _dict = eval(payload)
        except:
            # unexpected invalid_command or something else, ignore that line
            _dict = {}
        # just parse "recv" messages
        if 'recv' in _dict:
            # print "RECV"
            return parse_dict_recv(node_id, _dict)


def parse_dict_recv(rx_node, _dict):
    packet_count = 0
    rssi_sum = 0
    rssi_avg = 0
    lqi_sum = 0
    lqi_avg = 0
    nb_packets = _dict['nbPacket']
    tx_node = _dict['id']

    for item in _dict['recv']:
        seq = item[0]
        rssi = item[1]
        lqi = item[2]
        if seq >= 0 and seq < 100:
            packet_count = packet_count + 1
            rssi_sum = rssi_sum + rssi
            lqi_sum = lqi_sum + lqi

    if nb_packets != 0 and packet_count != 0:
        rssi_avg = rssi_sum / packet_count
        lqi_avg = lqi_sum / packet_count

    return_value = [int(rx_node),
                    int(tx_node),
                    int(nb_packets),
                    int(packet_count),
                    int(rssi_avg),
                    int(lqi_avg)]
    # print("rx_node:%s tx_node:%s nbPacket:%s
    # countPacket:%s RSSI:%s LQI:%s"
    # % (rx_node, tx_node, nb_packets,
    # packet_count, rssi_avg, lqi_avg))
    return np.array([return_value])
