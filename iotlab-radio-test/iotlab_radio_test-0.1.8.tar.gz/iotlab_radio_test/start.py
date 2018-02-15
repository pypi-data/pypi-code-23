from __future__ import print_function

import atexit
import logging
import socket
import subprocess
import time

import pkg_resources
import psutil
from iotlabcli import experiment, auth, Api
from iotlabcli.helpers import ACTIVE_STATES

from iotlab_radio_test.constants import FIRMWARE_PATH, SERIAL_AGGREGATOR
from iotlab_radio_test.utils import yes_no


def bind(executed):
    cmd = "socat TCP-LISTEN:0,fork,reuseaddr %s" % executed
    logging.info('Trying to start a socat, command %s' % cmd)
    process = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=True, stderr=True)
    time.sleep(1)
    process_children = psutil.Process(process.pid).children()
    if len(process_children) == 1:
        ps_connections = process_children[0].connections()
        if len(ps_connections) == 1:
            ps_port = ps_connections[0].laddr.port
            logging.info('OK socat running, redirecting to local port %u', ps_port)
            return process, ps_port
        else:
            logging.error('no connections in socat subprocess')
    else:
        logging.error('socat subprocess died unexpectedly')

    logging.error('socat subprocess failed to start')
    exit(-1)


def cleanup(api, experiment_id):
    experiment_state = experiment.get_experiment(api, experiment_id, 'state')['state']

    if experiment_state in ACTIVE_STATES:
        experiment.stop_experiment(api, experiment_id)
        logging.info('experiment %u stopped', experiment_id)
    else:
        logging.info('experiment %u already non-active', experiment_id)


def get_api():
    username, password = auth.get_user_credentials()

    return Api(username, password)


def submit_experiment(config, start_time=None):
    api = get_api()

    firmware = pkg_resources.resource_filename('iotlab_radio_test', FIRMWARE_PATH)

    nodes_list = ['m3-%u.%s.iot-lab.info' % (num, config.site) for num in
                  config.node_list]

    exp_d = [experiment.exp_resources(nodes_list, firmware)]

    data = experiment.submit_experiment(api, 'radio_test',
                                        start_time=start_time,
                                        duration=config.duration,
                                        resources=exp_d)

    return data['id']


def start_main(config, start_time):
    username, _ = auth.get_user_credentials()
    custom_api_url = Api.url
    if config.site is not None:
        cmd_format = '\"exec:ssh %s@%s.iot-lab.info \'env IOTLAB_API_URL=%s %s\'\"'
        cmd_serial_aggregator = cmd_format % (username, config.site, custom_api_url, SERIAL_AGGREGATOR)
    else:
        cmd_serial_aggregator = '\"exec:%s\"' % SERIAL_AGGREGATOR
        config.site = socket.gethostname()

    expected_qsize = len(config.node_list) * len(config.radio.txpower_list) * len(config.radio.channel_list)
    expected_duration = 7 * expected_qsize/60

    print('Expected duration with 7s per step, %u x %u x %u steps: %u minutes' %
          (len(config.node_list), len(config.radio.txpower_list), len(config.radio.channel_list), expected_duration))
    if config.duration is None:
        logging.info('No duration passed in config, using the expected duration %u minutes' % expected_duration)
        if not yes_no('is this OK?'):
            exit(0)
        config.duration = expected_duration
    if expected_duration > config.duration:
        if not yes_no('Are you sure to continue with the given duration, %u minutes ?' % config.duration):
            exit(0)

    api = get_api()
    experiment_id = submit_experiment(config, start_time)

    # proper cleanup of the experiment in case of abort
    atexit.register(cleanup, api, experiment_id)

    print('experiment submitted: %u' % experiment_id)

    print('waiting for the experiment to be running...')
    experiment.wait_experiment(api, experiment_id)

    running_experiment = experiment.get_experiment(api, experiment_id)
    deploymentresults = running_experiment['deploymentresults']
    successful_deployment = deploymentresults['0']
    successful_deployment_node_ids = [int(el.split('.')[0].split('-')[-1]) for el in successful_deployment]
    config.node_list = successful_deployment_node_ids

    print('Starting the socat...')
    # start the background port forwarding with socat

    socat, port = bind(cmd_serial_aggregator)
    print('socat subprocess port: %s' % port)

    # cleanup the background socat
    atexit.register(socat.kill)

    # check the socat subprocess before continuing
    time.sleep(1)
    if socat.poll() is not None:
        print('ERROR, socat subprocess didn\'t start properly')
        experiment.stop_experiment(api, experiment_id)
        exit(-1)

    return experiment_id, port
