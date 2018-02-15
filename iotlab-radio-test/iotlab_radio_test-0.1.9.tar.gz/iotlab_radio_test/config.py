from __future__ import print_function

import argparse
import os

import yaml

from iotlab_radio_test.constants import NOMINAL_CONFIG_FILE, LOG_DIR, RAW_DIR, PARSED_DIR, IMAGE_DIR
from iotlab_radio_test.utils import flatten, string_represents_integer, Config
from iotlab_radio_test.utils import get_or_create_dir
from iotlab_radio_test.utils import unflatten
from iotlab_radio_test.valid import VALID_CONFIG_SCHEMA, validate_config, valid_experiment_id


def get_exp_dir(experiment_id, experiments_dir=LOG_DIR, create=True):
    return get_or_create_dir(os.path.join(experiments_dir, str(experiment_id)), create)


def get_raw_dir(exp_dir, create=True):
    return get_or_create_dir(os.path.join(exp_dir, RAW_DIR), create)


def get_parsed_dir(exp_dir, create=True):
    return get_or_create_dir(os.path.join(exp_dir, PARSED_DIR), create)


def get_image_dir(exp_dir, create=True):
    return get_or_create_dir(os.path.join(exp_dir, IMAGE_DIR), create)


def get_config_file(exp_dir):
    return os.path.join(exp_dir, 'config.yaml')


def get_port_file(exp_dir):
    return os.path.join(exp_dir, 'port')


def write_config_to_yaml(config, config_file):
    with open(config_file, 'w') as stream:
        yaml.dump(config.to_dict(), stream)


def get_config_from_yaml(config_file=NOMINAL_CONFIG_FILE):
    with open(config_file, 'r') as stream:
        yaml_content = yaml.load(stream)
        if yaml_content is not None:
            return validate_config(yaml_content)


def filter_config_args(input_dict):
    flattened_valid_config = flatten(VALID_CONFIG_SCHEMA)
    flattened = flatten(input_dict)
    config_dict = {}
    non_config_dict = {}
    for key, value in flattened.items():
        if key in flattened_valid_config:
            config_dict[key] = value
        else:
            non_config_dict[key] = value

    return unflatten(config_dict), unflatten(non_config_dict)


def get_latest_experiment(experiments_dir=LOG_DIR):
    experiment_ids = []
    if os.path.exists(experiments_dir):
        for child in os.listdir(experiments_dir):
            try:
                if string_represents_integer(child) and valid_experiment_id(child):
                    experiment_ids.append(int(child))
            except argparse.ArgumentTypeError:
                pass
        try:
            return max(experiment_ids)
        except ValueError:
            return
