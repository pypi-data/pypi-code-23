from __future__ import print_function

import argparse
import logging
import os
from argparse import ArgumentParser

import yaml

from iotlab_radio_test.aggregate_exp_avg import AvgLogParser
from iotlab_radio_test.aggregate_stability import StabilityLogParser
from iotlab_radio_test.clean import CleanLog
from iotlab_radio_test.config import (get_exp_dir,
                                      get_config_file,
                                      get_latest_experiment,
                                      get_parsed_dir,
                                      get_image_dir,
                                      get_raw_dir,
                                      filter_config_args,
                                      get_config_from_yaml, get_port_file, write_config_to_yaml)
from iotlab_radio_test.connectivity_parser import ConnectivityLogParser
from iotlab_radio_test.constants import NOMINAL_CONFIG_FILE, METRIC_CHOICES, LOG_DIR
from iotlab_radio_test.draw_common import DrawArgs
from iotlab_radio_test.image_generator import ImageGenerator
from iotlab_radio_test.raw_log_parser import RowLogFileParser
from iotlab_radio_test.run import (run_main)
from iotlab_radio_test.start import get_api, start_main
from iotlab_radio_test.utils import flatten, Config
from iotlab_radio_test.valid import (VALID_CONFIG_SCHEMA,
                                     valid_experiment_id, ArgsList)


class ConfigArgumentParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ConfigArgumentParser, self).__init__(*args, **kwargs)
        validate = flatten(VALID_CONFIG_SCHEMA)

        def generate_arguments():
            for k, v in validate.items():
                returnvalue = {'args': ('--%s' % k,)}
                split = k.split('.')
                if isinstance(v.type, ArgsList):
                    returnvalue['kwargs'] = {'nargs':'*',
                                             'type': v.type.item_type,
                                             'metavar': v.type.element_name.upper()}
                else:
                    returnvalue['kwargs'] = {'type': v.type,
                                             'metavar': split[-1].upper()}
                returnvalue['kwargs']['help'] = v.description
                yield returnvalue

        for argument in generate_arguments():
            self.add_argument(*argument.get('args', []), **argument.get('kwargs', {}))

        self.add_argument('--config', dest='config', metavar='config_file_path')

    def parse_args(self, *args, **kwargs):
        parsed_args = super(ConfigArgumentParser, self).parse_args(*args, **kwargs)

        config_args_dict, non_config_args_dict = filter_config_args(vars(parsed_args))
        config_args_dict['node_list'] = config_args_dict.pop('nodes_str')

        cli_config = Config.from_dict(config_args_dict)
        if 'experiment_id' in non_config_args_dict:
            exp_dir = get_exp_dir(non_config_args_dict['experiment_id'])
            nominal_cfg_file = get_config_file(exp_dir)
            if not os.path.exists(nominal_cfg_file):
                nominal_cfg_file = NOMINAL_CONFIG_FILE
        else:
            nominal_cfg_file = NOMINAL_CONFIG_FILE

        nominal_config = get_config_from_yaml(nominal_cfg_file)

        cli_config_path = non_config_args_dict.pop('config')
        if cli_config_path is not None:
            cli_config__config = get_config_from_yaml(cli_config_path)

            if cli_config__config is None:
                self.error('invalid config file was passed')

            merged_config = nominal_config.merge(cli_config__config).merge(cli_config)
        else:
            merged_config = nominal_config.merge(cli_config)

        print('Config used:')
        print('------------')
        print(yaml.dump(merged_config.to_dict()), end='')
        print('------------')

        final_args = argparse.Namespace(**non_config_args_dict)

        final_args.config = merged_config

        return final_args


common_parser = ArgumentParser(add_help=False)
common_parser.add_argument("-i", "--id",
                           dest="experiment_id",
                           type=valid_experiment_id,
                           default=get_latest_experiment(),
                           help="IoT-LAB experiment id")

list_parser = ArgumentParser(add_help=False)
list_parser.add_argument("-l", "--list", dest="expid_list",
                         default=[],
                         nargs='*',
                         type=valid_experiment_id,
                         required=True,
                         help="IoT-LAB experiment ids list, e.g. 10 11 23 115")
list_parser.add_argument("-n", "--name",
                         dest="name",
                         default="default",
                         required=True,
                         help="output dir name, e.g. 5expRuns")

draw_parser = ArgumentParser(add_help=False)
draw_parser.add_argument("-m", "--metric",
                         dest="metric",
                         default='pdr',
                         help="metric to draw",
                         choices=METRIC_CHOICES)
draw_parser.add_argument("-S", "--show-stability",
                         dest="stability",
                         action="store",
                         help="show stability")
draw_parser.add_argument("-r", "--robot",
                         dest="robot",
                         default=False,
                         action="store_true",
                         help="show robots")
draw_parser.add_argument("-c", "--cluster",
                         dest="cluster",
                         default=False,
                         action="store_true",
                         help="show clusters")
draw_parser.add_argument("-n", "--nodes",
                         dest="nodes",
                         default=False,
                         action="store_true",
                         help="show nodes")
draw_parser.add_argument("-w", "--wifi",
                         dest="wifi",
                         default=False,
                         action="store_true",
                         help="show Wi-Fi AP")
draw_parser.add_argument("-s", "--save",
                         dest="save",
                         default=False,
                         action="store_true",
                         help="save image as file")

raw_parser_parser = ArgumentParser(parents=[common_parser])
start_parser = ArgumentParser()
start_parser.add_argument('--start_time', required=False,
                          help="Linux epoch, When to start the experiment, otherwise the experiment is started ASAP")
run_parser = ArgumentParser(parents=[common_parser])
aggregate_avg_parser = ArgumentParser(parents=[list_parser])
aggregate_stability_parser = ArgumentParser(parents=[list_parser])
connectivity_parser = ArgumentParser(parents=[common_parser])
clean_parser = ArgumentParser(parents=[common_parser])
draw_parser = ArgumentParser(parents=[common_parser, draw_parser])


def start_handler(args):
    experiment_id, port = start_main(args.config, args.start_time)

    exp_dir = get_exp_dir(experiment_id)
    raw_dir = get_raw_dir(exp_dir)
    parsed_dir = get_parsed_dir(exp_dir)

    # write port and config.yaml
    open(get_port_file(exp_dir), 'w').write(str(port))
    write_config_to_yaml(args.config, get_config_file(exp_dir))

    print('starting 01_run_radio_test...')

    run_main(args.config, exp_dir, raw_dir, port)

    print('OK, all finished.')

    print('parsing the results...')

    raw_parser_main(args.config, raw_dir, parsed_dir)

    print('parsing the connectivity...')

    connectivity_main(args.config, parsed_dir)


def aggregate_avg_handler(args):
    aggregate_avg_main(args.config, LOG_DIR,
                       get_parsed_dir(get_exp_dir(args.name)),
                       args.expid_list, args.name)


def aggregate_stability_handler(args):
    aggregate_stability_main(args.config, LOG_DIR,
                             get_parsed_dir(get_exp_dir(args.name)),
                             args.expid_list, args.name)


def clean_handler(args):
    print('Handling experiment id %u' % args.experiment_id)
    exp_dir = get_exp_dir(args.experiment_id)
    image_dir = get_image_dir(exp_dir)
    parsed_dir = get_parsed_dir(exp_dir)
    clean_main(image_dir, parsed_dir)


def connectivity_handler(args):
    print('Handling experiment id %u' % args.experiment_id)
    exp_dir = get_exp_dir(args.experiment_id)
    connectivity_main(args.config, get_parsed_dir(exp_dir))


def draw_handler(args):
    print('Handling experiment id %u' % args.experiment_id)
    exp_dir = get_exp_dir(args.experiment_id)
    image_dir = get_image_dir(exp_dir)
    parsed_dir = get_parsed_dir(exp_dir)
    other_args = DrawArgs(args.metric, args.stability, args.save,
                          args.nodes, args.wifi, args.robot)
    draw_main(args.config, image_dir, parsed_dir, other_args)


def raw_parser_handler(args):
    print('Handling experiment id %u' % args.experiment_id)
    exp_dir = get_exp_dir(args.experiment_id)
    raw_parser_main(args.config, get_raw_dir(exp_dir),
                    get_parsed_dir(exp_dir))


def run_handler(args):
    print('Handling experiment id %u' % args.experiment_id)
    exp_dir = get_exp_dir(args.experiment_id)
    port_file = os.path.join(exp_dir, 'port')
    if os.path.exists(port_file):
        port = int(open(port_file, 'r').read())
    else:
        port = 9000
    run_main(args.config, exp_dir, get_raw_dir(exp_dir), port)


handlers = {
    'start': start_handler,
    'run': run_handler,
    'raw_parser': raw_parser_handler,
    'aggregate_avg': aggregate_avg_handler,
    'aggregate_stability': aggregate_stability_handler,
    'connectivity': connectivity_handler,
    'draw': draw_handler,
    'clean': clean_handler
}

subparsers_dict = {
    'start': start_parser,
    'run': run_parser,
    'raw_parser': raw_parser_parser,
    'aggregate_avg': aggregate_avg_parser,
    'aggregate_stability': aggregate_stability_parser,
    'connectivity': connectivity_parser,
    'draw': draw_parser,
    'clean': clean_parser
}

parser = ConfigArgumentParser(add_help=False)
# parser.add_argument('command', help='commands')

subparsers = parser.add_subparsers(help='commands', dest='command')

subparsers.add_parser('start', parents=[start_parser], add_help=False)
subparsers.add_parser('run', parents=[run_parser], add_help=False)
subparsers.add_parser('raw_parser', parents=[raw_parser_parser], add_help=False)
subparsers.add_parser('aggregate_avg', parents=[aggregate_avg_parser], add_help=False)
subparsers.add_parser('aggregate_stability', parents=[aggregate_stability_parser], add_help=False)
subparsers.add_parser('connectivity', parents=[connectivity_parser], add_help=False)
subparsers.add_parser('draw', parents=[draw_parser], add_help=False)
subparsers.add_parser('clean', parents=[clean_parser], add_help=False)


def aggregate_avg_main(config, experiments_dir, output_dir, expid_list, name):
    api = get_api()
    avg_log_parser = AvgLogParser(config, api, experiments_dir, output_dir, expid_list, name)

    logging.info("Parsing IoT-LAB raw logs for experiment %s", expid_list)
    for channel in config.radio.channel_list:
        for txpower in config.radio.txpower_list:
            avg_log_parser.parse_file(channel, txpower)


def aggregate_stability_main(config, experiments_dir, output_dir, expid_list, output_name):
    stab_log_parser = StabilityLogParser(config, experiments_dir,
                                         output_dir, expid_list,
                                         output_name)
    print(stab_log_parser.expid_list)

    try:
        logging.info("Load links matrix and find stable links accross experiments %s", expid_list)
        # Bootstrap results array with 2 first experiments comparison
        experiment0 = stab_log_parser.expid_list[0]
        experiment1 = stab_log_parser.expid_list[1]
        for txpower in config.radio.txpower_list:
            stab_log_parser.parse_file(txpower, experiment0, experiment1)

        for experiment0 in stab_log_parser.expid_list:
            for txpower in config.radio.txpower_list:
                stab_log_parser.parse_file(txpower, experiment0)
        stab_log_parser.print_stats()
        stab_log_parser.save_results()

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt")


def clean_main(image_dir, parsed_dir):
    log_parser = CleanLog(parsed_dir, image_dir)
    logging.info("Cleaning parsed/image exp dir %s and %s", parsed_dir, image_dir)
    log_parser.clean_dir()


def connectivity_main(config, parsed_dir):
    logging.info("Parsing IoT-LAB merge logs from %s", parsed_dir)
    for txpower in config.radio.txpower_list:
        conn_log_parser = ConnectivityLogParser(config, parsed_dir, txpower)
        for channel in config.radio.channel_list:
            conn_log_parser.parse_file(channel)
        conn_log_parser.print_stats()
        conn_log_parser.save_results()


def draw_main(config, image_dir, parsed_dir, other_args):
    api = get_api()
    img_generator = ImageGenerator(config, api, image_dir, parsed_dir)

    logging.info("Generate IoT-LAB images for directory %s", parsed_dir)
    if other_args.metric == "connectivity":
        for txpower in config.radio.txpower_list:
            img_generator.parse_file(0, txpower, other_args.metric, other_args.stability)
    else:
        for channel in config.radio.channel_list:
            for txpower in config.radio.txpower_list:
                img_generator.parse_file(channel, txpower, other_args.metric, other_args.stability)
    img_generator.draw_image(other_args.nodes, other_args.wifi, other_args.robot)
    img_generator.save_image(other_args.save)


def raw_parser_main(config, raw_dir, parsed_dir):
    log_parser = RowLogFileParser(raw_dir, parsed_dir)

    logging.info("Parsing IoT-LAB raw logs from %s to %s", raw_dir, parsed_dir)
    for channel in config.radio.channel_list:
        for txpower in config.radio.txpower_list:
            log_parser.parse_file(config, channel, txpower)


def main():
    logging.basicConfig(level=logging.DEBUG)
    try:
        arguments = parser.parse_args()
        handlers[arguments.command](arguments)
        print('OK finished command \"%s\" successfully' % arguments.command)
    except KeyboardInterrupt:
        print("Keyboard interrupt")


if __name__ == '__main__':
    main()
