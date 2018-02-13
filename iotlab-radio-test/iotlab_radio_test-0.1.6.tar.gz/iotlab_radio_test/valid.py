import argparse
import json

import os

from iotlabcli import experiment
from iotlabcli.parser.common import check_site_with_server, expand_short_nodes_list

from iotlab_radio_test.utils import Config
from iotlab_radio_test.start import get_api
from iotlab_radio_test.utils import flatten, unflatten


def args_list__(typ):
    def func(input_string):
        try:
            return [typ(el) for el in input_string.split(',')]
        except:
            # entry of the list directly
            if not isinstance(input_string, basestring):
                return [typ(el) for el in input_string]
            msg = 'input %s could not be parsed as a list of %s' % (input_string, typ)
            raise argparse.ArgumentTypeError(msg)

    return func


class ArgsList(object):
    def __init__(self, item_type, element_name):
        self.item_type = item_type
        self.element_name = element_name

    def __call__(self, input):
        try:
            return [self.item_type(el) for el in input]
        except:
            msg = 'input %s could not be parsed as a list of %s' % (input, self.item_type)
            raise argparse.ArgumentTypeError(msg)


def valid_archi(archi):
    data = experiment.info_experiment(get_api(), archi=archi)
    if not data['items']:
        raise argparse.ArgumentTypeError('archi %s is not found in the API' % archi)
    else:
        return archi


def valid_channel(channel):
    if 11 <= int(channel) <= 26:
        return int(channel)
    else:
        raise argparse.ArgumentTypeError('channel %s is not valid, 11<=channel<=26' % channel)


def valid_txpower(txpower):
    tx_powers = [-17, -12, -9, -7, -5, -4, -3, -2, -1, 0, 0.7, 1.3, 1.8, 2.3, 3]
    if float(txpower) in tx_powers:
        return float(txpower)
    else:
        msg = 'txpower %s is not valid, should be one from %s'
        msg %= (txpower, ','.join(map(str, tx_powers)))
        raise argparse.ArgumentTypeError(msg)


def valid_experiment_id(experiment_id):
    from iotlab_radio_test.config import get_exp_dir, get_raw_dir
    exp_dir = get_exp_dir(experiment_id, create=False)

    if os.path.exists(exp_dir) \
            and os.listdir(exp_dir) \
            and os.path.exists(get_raw_dir(exp_dir, create=False)):
        return int(experiment_id)
    else:
        msg = '%s is not a valid experiment id' % experiment_id
        raise argparse.ArgumentTypeError(msg)


def valid_xyznameobject(input_str):
    obj_dict = json.loads(input_str)
    if set(obj_dict.keys()) == {'X', 'Y', 'Z', 'Name'}:
        return obj_dict
    else:
        msg = 'Robot or Wifi AP object should have X, Y, Z, Name attributes'
        raise argparse.ArgumentTypeError(msg)


def valid_nodes_str(nodes_str):
    try:
        return expand_short_nodes_list(str(nodes_str))
    except ValueError, e:
        raise argparse.ArgumentTypeError(e.message)


def valid_site(input_name):
    check_site_with_server(input_name)
    return input_name


class Argument(object):
    def __init__(self, type, description=''):
        self.type = type
        self.description = description


VALID_CONFIG_SCHEMA = {
    'site': Argument(valid_site, 'IoT-Lab site to use, can keep it empty when run on a site\'s SSH frontend'),
    'archi': Argument(valid_archi, 'Architecture of open-node '),
    'nodes_str': Argument(valid_nodes_str, 'list of nodes, e.g. 1+4-6'),
    'duration': Argument(int, 'duration of the experiment in minutes'),
    'radio': {
        'packet_size': Argument(int, 'packet size '),
        'packet_numbers': Argument(int, 'packet numbers'),
        'packet_interval': Argument(int, 'packet interval'),
        'channel_list': Argument(ArgsList(valid_channel, 'channel'), 'radio channel to use'),
        'txpower_list': Argument(ArgsList(valid_txpower, 'txpower'), 'transmission power in dBm to use'),
    },
    'draw': {
        'elev': Argument(float, 'Elevation from which to draw'),
        'azim': Argument(float, 'Azimuth from which to draw'),
        'font_size': Argument(int, 'Font size in the drawing'),
        'robots': Argument(ArgsList(valid_xyznameobject, 'robot_XYZName'),
                           'JSON description (X,Y,Z, Name dictionary) of the robots'),
        'wifi': Argument(ArgsList(valid_xyznameobject, 'wifi_XYZName'),
                         'JSON description (X,Y,Z, Name dictionary) of the wifi APs'),
    }
}


def validate_config(input_config, delete_none_values=False):
    flattened = flatten(input_config)
    if 'node_list' in flattened:
        flattened['nodes_str'] = '+'.join(str(el) for el in flattened.pop('node_list'))
    valid_flattened_config = flatten(VALID_CONFIG_SCHEMA)
    for key, value in flattened.items():
        if delete_none_values and value is None:
            del flattened[key]
        else:
            flattened[key] = valid_flattened_config[key].type(value)

    if 'nodes_str' in flattened:
        flattened['node_list'] = flattened.pop('nodes_str')
    return Config.from_dict(unflatten(flattened))
