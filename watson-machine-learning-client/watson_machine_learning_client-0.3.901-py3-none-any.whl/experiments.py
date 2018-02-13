################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

import requests
import json
import re
from watson_machine_learning_client.utils import get_headers
import time
import tqdm
import sys
from watson_machine_learning_client.wml_client_error import MissingValue, WMLClientError
from watson_machine_learning_client.href_definitions import is_uid
from watson_machine_learning_client.wml_resource import WMLResource
from multiprocessing import Pool
from watson_machine_learning_client.utils import print_text_header_h1, print_text_header_h2, EXPERIMENT_RUN_DETAILS_TYPE, format_metrics


class Experiments(WMLResource):
    """
       Run new experiment.
    """

    def __init__(self, client, wml_credentials, wml_token, instance_details):
        WMLResource.__init__(self, __name__, client, wml_credentials, wml_token, instance_details)
        self._experiments_uids_cache = {}

    def _get_experiment_uid(self, experiment_run_uid=None, experiment_run_url=None):
        if experiment_run_uid is None and experiment_run_url is None:
            raise MissingValue('experiment_run_id/experiment_run_url')

        if experiment_run_uid is not None and experiment_run_uid in self._experiments_uids_cache:
            return self._experiments_uids_cache[experiment_run_uid]

        if experiment_run_url is not None:
            m = re.search('.+/v3/experiments/{[^\/]+}/runs/{[^\/]+}', experiment_run_url)
            _experiment_id = m.group(1)
            _experiment_run_id = m.group(2)
            self._experiments_uids_cache.update({_experiment_run_id: _experiment_id})
            return _experiment_id

        details = self.get_details()

        resources = details['resources']

        try:
            el = [x for x in resources if x['metadata']['guid'] == experiment_run_uid][0]
        except Exception as e:
            raise WMLClientError('Cannot find experiment_uid for experiment_run_uid: \'{}\''.format(experiment_run_uid), e)

        experiment_uid = el['experiment']['guid']
        self._experiments_uids_cache.update({experiment_run_uid: experiment_uid})
        return experiment_uid

    def run(self, experiment_uid, asynchronous=True):
        """
            Run experiment.

            :param experiment_uid: ID of stored experiment
            :type experiment_uid: str
            :param asynchronous: Default `True` means that experiment is started and progress can be checked later. `False` - method will wait till experiment end and print experiment stats.
            :type asynchronous: bool

            :return: experiment run details
            :rtype: dict

            A way you might use me is

            >>> experiment_run_status = client.experiments.run(experiment_uid)
            >>> experiment_run_status = client.experiments.run(experiment_uid, asynchronous=False)
        """
        Experiments._validate_type(experiment_uid, 'experiment_uid', str, True)
        Experiments._validate_type(asynchronous, 'asynchronous', bool, True)

        run_url = self._href_definitions.get_experiment_runs_href(experiment_uid)

        response = requests.post(run_url, headers=get_headers(self._wml_token))

        # TODO should be 202
        result_details = self._handle_response(200, 'experiment run', response)

        experiment_run_uid = self.get_run_uid(result_details)
        self._experiments_uids_cache.update({experiment_run_uid: experiment_uid})

        if asynchronous:
            return result_details
        else:
            start = time.time()
            training_runs_names = [x['training_guid'] for x in result_details['entity']['training_statuses']]
            print_text_header_h1('Running \'{}\' experiment run'.format(experiment_run_uid))

            status = self.get_status(experiment_run_uid)
            state = status['state']

            i = 0
            for training_run_name in training_runs_names:
                i += 1
                print_text_header_h2('\'{}\' run ({}/{})'.format(training_run_name, i, len(training_runs_names)))

                j = 0
                while True:
                    j += 1
                    sys.stdout.flush()
                    for k in tqdm.tqdm(range(10)):
                        time.sleep(1)
                    # t = tqdm.tqdm(total=10, ascii=True, desc='Epoch ' + str(j))
                    # for i in range(10):
                    #     time.sleep(1)
                    #     t.update()
                    details = self.get_run_details(experiment_run_uid)
                    status = details['entity']['experiment_run_status']
                    state = status['state']
                    training_details = list(filter(lambda x: x['training_guid'] == training_run_name,
                                                   details['entity']['training_statuses']))[0]

                    elapsed_time = time.time() - start
                    print("Elapsed time: " + str(elapsed_time) + " -> training state: " + str(training_details['state']))
                    print('')
                    # t.set_postfix({
                    #     'elapsed_time': str(elapsed_time),
                    #     'training_state': training_details['state']
                    # })

                    if state == 'completed' or state == 'error' or state == 'canceled':
                        break

                    if training_details['state'] == 'completed' or training_details['state'] == 'error' or training_details['state'] == 'canceled':
                        break

            if 'completed' in state:
                print_text_header_h2('Run of \'{}\' finished successfully.'.format(str(experiment_run_uid)))
            else:
                print_text_header_h2(
                    'Run of \'{}\' failed with status: \'{}\'.'.format(experiment_run_uid, str(status)))

            # TODO probably details should be get one more time
            self._logger.debug('Response({}): {}'.format(state, result_details))
            return result_details

    def get_status(self, experiment_run_uid):
        """
            Get experiment status.

            :param experiment_run_uid: ID of experiment run
            :type experiment_run_uid: bool

            :returns: experiment status
            :rtype: dict

            A way you might use me is

            >>> experiment_status = client.experiments.get_status(experiment_run_uid)
        """
        Experiments._validate_type(experiment_run_uid, 'experiment_run_uid', str, True)
        details = self.get_run_details(experiment_run_uid)

        try:
            status = WMLResource._get_required_element_from_dict(details, 'details', ['entity', 'experiment_run_status'])
        except Exception as e:
            # TODO more specific
            raise WMLClientError('Failed to get from details state of experiment.', e)

        return status

    @staticmethod
    def _get_details_helper(url, headers, setting=None):
        from watson_machine_learning_client.log_util import get_logger
        logger = get_logger('experiments._get_details_helper')
        response_get = requests.get(
            url + '/runs',
            headers=headers)
        if response_get.status_code == 200:
            logger.debug('Successfully got runs details ({}): {}'.format(response_get.status_code, response_get.text))
            details = json.loads(response_get.text)

            if 'resources' in details:
                resources = details['resources']
            else:
                resources = [details]

            if setting is not None:
                for r in resources:
                    r['entity'].update({'_parent_settings': setting})
            return resources
        else:
            logger.warn('Failure during getting runs details ({}): {}'.format(response_get.status_code, response_get.text))
            return []

    def get_run_details(self, experiment_run_uid):
        """
           Get metadata of particular experiment run.

           :param experiment_run_uid:  experiment run UID
           :type experiment_run_uid: bool

           :returns: experiment run metadata
           :rtype: dict

           A way you might use me is

           >>> experiment_run_details = client.experiments.get_run_details(experiment_run_uid)
        """
        Experiments._validate_type(experiment_run_uid, 'experiment_run_uid', str, True)

        experiment_uid = self._get_experiment_uid(experiment_run_uid)

        url = self._href_definitions.get_experiment_run_href(experiment_uid, experiment_run_uid)

        response_get = requests.get(
            url,
            headers=get_headers(self._wml_token))
        response = self._handle_response(200, 'getting experiment run details', response_get)
        #setting = self._client.repository.get_experiment_details(experiment_uid)['entity']['settings']
        #response['entity'].update({'_parent_settings': setting})
        return response

    def get_details(self, experiment_uid=None):
        """
           Get metadata of experiment(s) run(s). If no experiment_uid is provided, runs will be listed for all existing experiments.

           :param experiment_uid:  experiment UID (optional)
           :type experiment_uid: bool

           :returns: experiment(s) run(s) metadata
           :rtype: dict

           A way you might use me is

           >>> experiment_details = client.experiments.get_details(experiment_uid)
           >>> experiment_details = client.experiments.get_details()
        """
        return self._get_extended_details(experiment_uid, False)

    @staticmethod
    def get_run_url(experiment_run_details):
        """
            Get experiment run url.

            :param experiment_run_details: details of experiment run
            :type experiment_run_details: object

            :returns: experiment run url
            :rtype: str

            A way you might use me is

            >>> experiment_run_url = client.experiments.get_run_url(experiment_run_details)
        """

        Experiments._validate_type(experiment_run_details, 'experiment_run_details', object, True)
        Experiments._validate_type_of_details(experiment_run_details, EXPERIMENT_RUN_DETAILS_TYPE)

        try:
            url = WMLResource._get_required_element_from_dict(experiment_run_details, 'experiment_run_details', ['metadata', 'url'])
        except Exception as e:
            raise WMLClientError('Failure during getting experiment run url from details.', e)

        # TODO uncomment
        # if not is_url(url):
        #     raise WMLClientError('Experiment url: \'{}\' is invalid.'.format(url))

        return url

    @staticmethod
    def get_run_uid(experiment_run_details):
        """
            Get experiment run uid.

            :param experiment_run_details: details of experiment run
            :type experiment_run_details: object

            :returns: experiment run uid
            :rtype: str

            A way you might use me is

            >>> experiment_run_uid = client.experiments.get_run_uid(experiment_run_details)
        """

        Experiments._validate_type(experiment_run_details, 'experiment_run_details', object, True)
        Experiments._validate_type_of_details(experiment_run_details, EXPERIMENT_RUN_DETAILS_TYPE)

        try:
            uid = WMLResource._get_required_element_from_dict(experiment_run_details, 'experiment_run_details', ['metadata', 'guid'])
        except Exception as e:
            raise WMLClientError('Failure during getting experiment run uid from details.', e)

        if not is_uid(uid):
            raise WMLClientError('Experiment run uid: \'{}\' is invalid.'.format(uid))

        return uid

    @staticmethod
    def get_training_runs(experiment_run_details):
        """
            Get experiment training runs details.

            :param experiment_run_details: details of experiment run
            :type: object

            :returns: training runs
            :rtype: array

            A way you might use me is

            >>> training_runs = client.experiments.get_training_runs(experiment_run_details)
        """

        Experiments._validate_type(experiment_run_details, 'experiment_run_details', object, True)
        Experiments._validate_type_of_details(experiment_run_details, EXPERIMENT_RUN_DETAILS_TYPE)

        # TODO probably should be just entity.guid
        try:
            training_runs = WMLResource._get_required_element_from_dict(experiment_run_details, 'experiment_run_details',
                                                              ['entity', 'training_statuses'])
        except Exception as e:
            raise WMLClientError('Failure during getting experiment training runs from details.', e)

        if training_runs is None or len(training_runs) <= 0:
            raise MissingValue('training_runs')

        return training_runs

    @staticmethod
    def get_training_uids(experiment_run_details):
        """
            Get experiment training uids.

            :param experiment_run_details: details of experiment run
            :type experiment_run_details: object

            :returns: training uids
            :rtype: array

            A way you might use me is

            >>> training_uids = client.experiments.get_training_uids(experiment_run_details)
        """

        Experiments._validate_type(experiment_run_details, 'experiment_run_details', object, True)
        Experiments._validate_type_of_details(experiment_run_details, EXPERIMENT_RUN_DETAILS_TYPE)

        # TODO probably should be just entity.guid
        try:
            training_uids = [x['training_guid'] for x in WMLResource._get_required_element_from_dict(experiment_run_details,
                                                                        'experiment_run_details',
                                                                        ['entity', 'training_statuses'])]
        except Exception as e:
            raise WMLClientError('Failure during getting experiment training runs from details.', e)

        if training_uids is None or len(training_uids) <= 0:
            raise MissingValue('training_uids')

        return training_uids

    def delete(self, experiment_run_uid):
        """
            Delete experiment run.

            :param experiment_run_uid:  experiment run UID
            :type experiment_run_uid: str

            A way you might use me is

            >>> client.experiments.delete(experiment_run_uid)
        """
        Experiments._validate_type(experiment_run_uid, 'experiment_run_uid', str, True)

        experiment_uid = self._get_experiment_uid(experiment_run_uid)

        run_url = self._href_definitions.get_experiment_run_href(experiment_uid, experiment_run_uid)

        response = requests.delete(run_url, headers=get_headers(self._wml_token))

        self._handle_response(204, 'experiment deletion', response, False)

    def _get_extended_details(self, experiment_uid=None, extended=True):
        Experiments._validate_type(experiment_uid, 'experiment_uid', str, False)

        if experiment_uid is None:
            experiments = self._client.repository.get_experiment_details()

            try:
                urls_and_settings = [(experiment['metadata']['url'], experiment['entity']['settings'] if extended else None) for experiment in
                                     experiments['resources']]

                self._logger.debug('Preparing details for urls and settings: {}'.format(urls_and_settings))

                res = []

                with Pool(processes=4) as pool:
                    tasks = []
                    for url_and_setting in urls_and_settings:
                        url = url_and_setting[0]
                        setting = url_and_setting[1]
                        tasks.append(pool.apply_async(Experiments._get_details_helper,
                                                      (url, get_headers(self._wml_token), setting)))

                    for task in tasks:
                        res.extend(task.get())

            except Exception as e:
                raise WMLClientError('Error during getting all experiments details.', e)
            return {"resources": res}
        else:
            url = self._href_definitions.get_experiment_runs_href(experiment_uid)

            response_get = requests.get(
                url,
                headers=get_headers(self._wml_token))
            # TODO should be 200
            result = self._handle_response(200, 'getting experiment details', response_get)
            setting = self._client.repository.get_experiment_details(experiment_uid)['entity']['settings']
            for r in result['resources']:
                r['entity'].update({'_parent_settings': setting})

            return result

    def list(self, experiment_uid=None):
        """
            List experiment runs.

            :param experiment_uid: experiment UID (optional)
            :type experiment_uid: str

            A way you might use me is

            >>> client.experiments.list()
            >>> client.experiments.list(experiment_uid)
        """
        Experiments._validate_type(experiment_uid, 'experiment_uid', str, False)

        from tabulate import tabulate

        details = self._get_extended_details(experiment_uid, True)

        resources = details['resources']

        values = [(m['experiment']['guid'], m['metadata']['guid'], m['entity']['_parent_settings']['name'], m['entity']['experiment_run_status']['state'], m['metadata']['created_at']) for m in resources]
        table = tabulate([["GUID (experiment)", "GUID (run)", "NAME (experiment)", "STATE", "CREATED"]] + values)
        print(table)

    def list_training_runs(self, experiment_run_uid):
        """
             List training runs triggered by experiment run.

             :param experiment_run_uid: experiment run UID
             :type experiment_run_uid: str

             A way you might use me is

             >>> client.experiments.list_training_runs(experiment_run_uid)
         """
        Experiments._validate_type(experiment_run_uid, 'experiment_run_uid', str, True)

        from tabulate import tabulate
        details = self._client.experiments.get_run_details(experiment_run_uid)
        training_statuses = details['entity']['training_statuses']

        values = [(m["training_guid"], m['training_reference_name'], m['state'], m['submitted_at'], m['finished_at'],
                   format_metrics(self._client.training.get_latest_metrics(m['training_guid']))) for m in training_statuses]

        table = tabulate([["GUID (training)", "NAME", "STATE", "SUBMITTED", "FINISHED", "PERFORMANCE"]] + values)

        print(table)

    def monitor_logs(self, experiment_run_uid):
        """
            Monitor experiment run log files (prints log content to console).

            :param experiment_run_uid: ID of experiment run
            :type experiment_run_uid: str

            A way you might use me is

            >>> client.experiments.monitor_logs(experiment_run_uid)
        """
        Experiments._validate_type(experiment_run_uid, 'experiment_run_uid', str, True)

        try:
            experiment_uid = self.get_run_details(experiment_run_uid)['experiment']['guid']
        except Exception as e:
            raise WMLClientError('Failure during getting experiment uid from experiment run details.', e)

        from lomond import WebSocket
        experiment_monitor_endpoint = self._wml_credentials['url'].replace('https',
                                                          'wss') + "/v3/experiments/" + experiment_uid + '/runs/' + experiment_run_uid + "/monitor"
        websocket = WebSocket(experiment_monitor_endpoint)
        websocket.add_header(bytes("Authorization", "utf-8"), bytes("bearer " + self._wml_token, "utf-8"))

        print_text_header_h1("Monitor started for experiment run: " + str(experiment_run_uid))

        previous_guid = ''

        for event in websocket:
            if event.name == 'text':
                text = json.loads(event.text)
                if ('entity' in str(text)) and ('training_statuses' in str(text)):
                    training_statuses = text['entity']['training_statuses']
                    for i in training_statuses:
                        if ('training_guid' in str(i)) and ('message' in str(i)):
                            msg = i['message'].strip()
                            guid = i["training_guid"].strip()
                            if msg != '':
                                if guid == previous_guid:
                                    print(msg)
                                else:
                                    print_text_header_h2(guid)
                                    print(msg)

                                previous_guid = guid

        print_text_header_h2('Log monitor done.')

    def monitor_metrics(self, experiment_run_uid):
        """
            Monitor metrics log file (prints metrics to console).

            :param experiment_run_uid: ID of experiment run
            :type run_uid: str

            A way you might use me is:

            >>> client.experiments.monitor_metrics(experiment_run_uid)
        """

        try:
            experiment_uid = self.get_run_details(experiment_run_uid)['experiment']['guid']
        except Exception as e:
            raise WMLClientError('Failure during getting experiment uid from experiment run details.', e)

        print_text_header_h1("Metric monitor started for experiment run: " + str(experiment_run_uid))

        from lomond import WebSocket
        experiment_monitor_endpoint = self._wml_credentials['url'].replace('https',
                                                                     'wss') + "/v3/experiments/" + experiment_uid + '/runs/' + experiment_run_uid + "/monitor"
        websocket = WebSocket(experiment_monitor_endpoint)
        websocket.add_header(bytes("Authorization", "utf-8"), bytes("bearer " + self._wml_token, "utf-8"))

        previous_guid = ''

        for event in websocket:
            if event.name == 'text':
                text = json.loads(event.text)
                if ('entity' in str(text)) and ('training_statuses' in str(text)):
                    training_statuses = text['entity']['training_statuses']

                    for i in training_statuses:
                        if 'training_guid' in str(i):
                            guid = i["training_guid"].strip()

                            if ('metrics' in str(i)) and ('current_iteration' in str(i)):
                                metrics = i['metrics']
                                if len(metrics) > 0:
                                    metric = metrics[0]
                                    values = ''
                                    for x in metric['values']:
                                        values = values + x['name'] + ':' + str(x['value']) + ' '

                                    metric_msg = metric['timestamp'] + ' ' + 'iteration:' + str(i['current_iteration']) + ' phase:' + metric['phase'] + ' ' + values

                                    if metric_msg != '':
                                        if guid == previous_guid:
                                            print(metric_msg)
                                        else:
                                            print_text_header_h2(guid)
                                            print(metric_msg)

                                        previous_guid = guid

        print_text_header_h2('Metric monitor done.')
