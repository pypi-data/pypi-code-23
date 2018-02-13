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
from watson_machine_learning_client.utils import get_headers, print_text_header_h1, print_text_header_h2, TRAINING_RUN_DETAILS_TYPE
import time
import tqdm
from watson_machine_learning_client.metanames import TrainingConfigurationMetaNames
import sys
from watson_machine_learning_client.wml_client_error import WMLClientError
from watson_machine_learning_client.href_definitions import is_uid, is_url
from watson_machine_learning_client.wml_resource import WMLResource


class Training(WMLResource):
    """
       Train new models.
    """

    def __init__(self, client, wml_credentials, wml_token, instance_details):
        WMLResource.__init__(self, __name__, client, wml_credentials, wml_token, instance_details)
        self._base_models_url = wml_credentials['url'] + "/v3/models"
        self.ConfigurationMetaNames = TrainingConfigurationMetaNames()

    @staticmethod
    def _is_training_uid(s):
        res = re.match('training\-[a-zA-Z0-9\-\_]+', s)
        return res is not None

    @staticmethod
    def _is_training_url(s):
        res = re.match('\/v3\/models\/training\-[a-zA-Z0-9\-\_]+', s)
        return res is not None

    # def get_frameworks(self):
    #     """
    #        Get list of supported frameworks.
    #
    #        :returns: supported frameworks for training
    #        :rtype: json
    #
    #        A way you might use me is:
    #
    #        >>> model_details = client.training.get_frameworks()
    #     """
    #
    #     response_get = requests.get(self._base_models_url + "/frameworks", headers=get_headers(self._wml_token))
    #
    #     if response_get.status_code == 200:
    #         return json.loads(response_get.text)
    #     else:
    #         error_msg = 'Getting supported frameworks failed.' + '\n' + "Error msg: " + response_get.text
    #         print(error_msg)
    #         return None

    def get_status(self, run_uid):
        """
              Get training status.

              :param run_uid: ID of trained model
              :type run_uid: str

              :returns: training run status
              :rtype: dict

              A way you might use me is:

              >>> training_status = client.training.get_status(run_uid)
        """
        Training._validate_type(run_uid, 'run_uid', str, True)

        details = self.get_details(run_uid)

        if details is not None:
            return WMLResource._get_required_element_from_dict(details, 'details', ['entity', 'status'])
        else:
            raise WMLClientError('Getting trained model status failed. Unable to get model details for run_uid: \'{}\'.'.format(run_uid))

    def get_details(self, run_uid=None):
        """
              Get trained model details.

              :param run_uid: ID of trained model (optional, if not provided all runs details are returned)
              :type run_uid: str

              :returns: training run(s) details
              :rtype: dict

              A way you might use me is:

              >>> trained_model_details = client.training.get_details(run_uid)
              >>> trained_models_details = client.training.get_details()
        """
        Training._validate_type(run_uid, 'run_uid', str, False)

        if run_uid is None:
            response_get = requests.get(self._base_models_url, headers=get_headers(self._wml_token))

            return self._handle_response(200, 'getting trained models details', response_get)
        else:
            get_details_endpoint = '{}/v3/models/'.format(self._wml_credentials['url']) + run_uid
            model_training_details = requests.get(get_details_endpoint, headers=get_headers(self._wml_token))

            return self._handle_response(200, 'getting trained models details', model_training_details)

    @staticmethod
    def get_run_url(run_details):
        """
            Get training run url from training run details.

            :param run_details:  Created training run details
            :type run_details: dict

            :returns: training run URL that is used to manage the training
            :rtype: str

            A way you might use me is:

            >>> run_url = client.training.get_run_url(run_details)
        """
        Training._validate_type(run_details, 'run_details', object, True)
        Training._validate_type_of_details(run_details, TRAINING_RUN_DETAILS_TYPE)
        return WMLResource._get_required_element_from_dict(run_details, 'run_details', ['metadata', 'url'])

    @staticmethod
    def get_run_uid(run_details):
        """
            Get uid of training run.

            :param run_details:  training run details
            :type run_details: dict

            :returns: uid of training run
            :rtype: str

            A way you might use me is:

            >>> model_uid = client.training.get_run_uid(run_details)
        """
        Training._validate_type(run_details, 'run_details', object, True)
        Training._validate_type_of_details(run_details, TRAINING_RUN_DETAILS_TYPE)
        return WMLResource._get_required_element_from_dict(run_details, 'run_details', ['metadata', 'guid'])

    def cancel(self, run_uid):
        """
              Cancel model training.

              :param run_uid: ID of trained model
              :type run_uid: str

              A way you might use me is:

              >>> client.training.cancel(run_uid)
        """
        Training._validate_type(run_uid, 'run_uid', str, True)

        patch_endpoint = self._base_models_url + '/' + str(run_uid)
        patch_payload = [
            {
                "op": "replace",
                "path": "/status/state",
                "value": "canceled"
            }
        ]

        response_patch = requests.patch(patch_endpoint, json=patch_payload, headers=get_headers(self._wml_token))

        self._handle_response(204, 'model training cancel', response_patch, False)
        return

    def run(self, definition_uid, meta_props, asynchronous=True):
        """
        Train new model.

        :param definition_uid: uid to saved model_definition/pipeline
        :type definition_uid: str

        :param meta_props: meta data of the training configuration. To see available meta names use:

            >>> client.training.ConfigurationMetaNames.show()

        :type meta_props: dict

        :param asynchronous: Default `True` means that training job is submitted and progress can be checked later.
               `False` - method will wait till job completion and print training stats.
        :type asynchronous: bool

        :returns: training run details
        :rtype: dict

        A way you might use me is:

        >>> metadata = {
        >>>  client.training.ConfigurationMetaNames.NAME: "Hand-written Digit Recognition",
        >>>  client.training.ConfigurationMetaNames.AUTHOR_EMAIL: "JohnSmith@js.com",
        >>>  client.training.ConfigurationMetaNames.TRAINING_DATA_REFERENCE: {
        >>>          "connection": {
        >>>              "endpoint_url": "https://s3-api.us-geo.objectstorage.service.networklayer.com",
        >>>              "aws_access_key_id": "***",
        >>>              "aws_secret_access_key": "***"
        >>>          },
        >>>          "source": {
        >>>              "bucket": "wml-dev",
        >>>          }
        >>>          "type": "s3"
        >>>      }
        >>> client.training.ConfigurationMetaNames.TRAINING_RESULTS_REFERENCE: {
        >>>          "connection": {
        >>>              "endpoint_url": "https://s3-api.us-geo.objectstorage.service.networklayer.com",
        >>>              "aws_access_key_id": "***",
        >>>              "aws_secret_access_key": "***"
        >>>          },
        >>>          "target": {
        >>>              "bucket": "wml-dev-results",
        >>>          }
        >>>          "type": "s3"
        >>>      },
        >>> }
        >>> run_details = client.training.run(definition_uid, meta_props=metadata)
        >>> run_uid = client.training.get_run_uid(run_details)
        """
        Training._validate_type(definition_uid, 'definition_uid', str, True)
        Training._validate_type(meta_props, 'meta_props', object, True)
        Training._validate_type(asynchronous, 'asynchronous', bool, True)
        self.ConfigurationMetaNames._validate(meta_props)

        if definition_uid is not None and is_uid(definition_uid):
            definition_url = self._href_definitions.get_definition_href(definition_uid)
        elif definition_uid is not None:
            raise WMLClientError('Invalid uid: \'{}\'.'.format(definition_uid))
        else:
            raise WMLClientError('Both uid and url are empty.')

        details = self._client.repository.get_definition_details(definition_uid)

        if self.ConfigurationMetaNames.FRAMEWORK_NAME not in meta_props:
            meta_props.update({self.ConfigurationMetaNames.FRAMEWORK_NAME: details['entity']['framework']['name']})

        if self.ConfigurationMetaNames.FRAMEWORK_VERSION not in meta_props:
            meta_props.update(
                {self.ConfigurationMetaNames.FRAMEWORK_VERSION: details['entity']['framework']['version']})

        if self.ConfigurationMetaNames.EXECUTION_COMMAND not in meta_props:
            meta_props.update(
                {self.ConfigurationMetaNames.EXECUTION_COMMAND: details['entity']['command']})

        training_configuration_metadata = {
            "model_definition": {
                "framework": {
                    "name": meta_props[self.ConfigurationMetaNames.FRAMEWORK_NAME],
                    "version": meta_props[self.ConfigurationMetaNames.FRAMEWORK_VERSION]
                },
                "name": meta_props[self.ConfigurationMetaNames.NAME],
                "author": {
                    "email": meta_props[self.ConfigurationMetaNames.AUTHOR_EMAIL]
                },
                "definition_href": definition_url,
                "execution": {
                    "command": meta_props[self.ConfigurationMetaNames.EXECUTION_COMMAND],
                    "resource": "small"
                }
            },
            "training_data_reference": meta_props[self.ConfigurationMetaNames.TRAINING_DATA_REFERENCE],
            "training_results_reference": meta_props[self.ConfigurationMetaNames.TRAINING_RESULTS_REFERENCE]
        }

        if self.ConfigurationMetaNames.DESCRIPTION in meta_props:
            training_configuration_metadata['model_definition'].update({'description': meta_props[self.ConfigurationMetaNames.DESCRIPTION]})

        if self.ConfigurationMetaNames.AUTHOR_NAME in meta_props:
            training_configuration_metadata['model_definition']['author'].update({'name': meta_props[self.ConfigurationMetaNames.AUTHOR_NAME]})

        # TODO uncomment if it will be truly optional in service
        # if self.ConfigurationMetaNames.FRAMEWORK_NAME in meta_props or self.ConfigurationMetaNames.FRAMEWORK_VERSION in meta_props:
        #     training_configuration_metadata['model_definition'].update({'framework': {}})
        #     if self.ConfigurationMetaNames.FRAMEWORK_NAME in meta_props:
        #         training_configuration_metadata['model_definition']['framework'].update({'name': meta_props[self.ConfigurationMetaNames.FRAMEWORK_NAME]})
        #     if self.ConfigurationMetaNames.FRAMEWORK_VERSION in meta_props:
        #         training_configuration_metadata['model_definition']['framework'].update({'version': meta_props[self.ConfigurationMetaNames.FRAMEWORK_VERSION]})

        # TODO uncomment if it will be truly optional in service
        # if self.ConfigurationMetaNames.EXECUTION_COMMAND in meta_props or self.ConfigurationMetaNames.EXECUTION_RESOURCE_SIZE in meta_props:
        #     training_configuration_metadata['model_definition'].update({'execution': {}})
        #     if self.ConfigurationMetaNames.EXECUTION_COMMAND in meta_props:
        #         training_configuration_metadata['model_definition']['execution'].update({'command': meta_props[self.ConfigurationMetaNames.EXECUTION_COMMAND]})
        if self.ConfigurationMetaNames.COMPUTE_CONFIGURATION in meta_props:
            training_configuration_metadata['model_definition']['execution']['computer_configuration'].update({'name': meta_props[self.ConfigurationMetaNames.COMPUTE_CONFIGURATION]})

        train_endpoint = '{}/v3/models'.format(self._wml_credentials['url'])

        response_train_post = requests.post(train_endpoint, json=training_configuration_metadata,
                                            headers=get_headers(self._wml_token))

        run_details = self._handle_response(202, 'training', response_train_post)

        trained_model_guid = self.get_run_uid(run_details)

        if asynchronous is True:
            return run_details
        else:
            start = time.time()
            print_text_header_h1('Running \'{}\''.format(trained_model_guid))

            status = self.get_status(trained_model_guid)
            state = status['state']

            # TODO add iterations progress based on details
            while ('completed' not in state) and ('error' not in state) and ('canceled' not in state):
                elapsed_time = time.time() - start
                print("Elapsed time: " + str(elapsed_time) + " -> training state: " + str(state))
                sys.stdout.flush()
                status = self.get_status(trained_model_guid)
                state = status['state']
                for i in tqdm.tqdm(range(10)):
                    time.sleep(1)

            if 'completed' in state:
                print('Training of \'{}\' finished successfully.'.format(str(trained_model_guid)))
            else:
                print('Training of \'{}\' failed with status: \'{}\'.'.format(trained_model_guid, str(status)))

            # TODO probably details should be get right before returning them
            self._logger.debug('Response({}): {}'.format(state, run_details))
            return run_details

    def list(self):
        """
           List training runs.

           A way you might use me is:

           >>> client.training.list()
        """
        from tabulate import tabulate

        details = self.get_details()
        resources = details['resources']
        values = [(m["metadata"]['guid'], m['entity']['model_definition']['name'], m["entity"]['status']['state'], m['metadata']['created_at'],
                   m['entity']['model_definition']['framework']['name']) for m in resources]
        table = tabulate([["GUID (training)", "NAME", "STATE", "CREATED", "FRAMEWORK"]] + values)
        print(table)

    def delete(self, run_uid):
        """
            Delete training run.

            :param run_uid: ID of trained model
            :type run_uid: str

            A way you might use me is:

            >>> trained_models_list = client.training.delete(run_uid)
        """
        Training._validate_type(run_uid, 'run_uid', str, True)

        response_delete = requests.delete(self._base_models_url + '/' + str(run_uid),
                                          headers=get_headers(self._wml_token))

        self._handle_response(204, 'trained model deletion', response_delete, False)

    def monitor_logs(self, run_uid):
        """
            Monitor training log file (prints log content to console).

            :param run_uid: ID of trained model
            :type run_uid: str

            A way you might use me is:

            >>> client.training.monitor_logs(run_uid)
        """
        Training._validate_type(run_uid, 'run_uid', str, True)

        from lomond import WebSocket

        monitor_endpoint = self._wml_credentials['url'].replace('https',
                                                                'wss') + "/v3/models/" + run_uid + "/monitor"
        websocket = WebSocket(monitor_endpoint)
        websocket.add_header(bytes("Authorization", "utf-8"), bytes("bearer " + self._wml_token, "utf-8"))

        print_text_header_h1("Log monitor started for training run: " + str(run_uid))

        for event in websocket:
            if event.name == 'text':
                text = json.loads(event.text)
                status = text['status']

                if 'message' in status:
                    print(status["message"])

        print_text_header_h2("Log monitor done.")

    def monitor_metrics(self, run_uid):
        """
            Monitor metrics log file (prints log content to console).

            :param run_uid: ID of trained model
            :type run_uid: str

            A way you might use me is:

            >>> client.training.monitor_metrics(run_uid)
        """
        Training._validate_type(run_uid, 'run_uid', str, True)

        from lomond import WebSocket

        monitor_endpoint = self._wml_credentials['url'].replace('https',
                                                                'wss') + "/v3/models/" + run_uid + "/monitor"
        websocket = WebSocket(monitor_endpoint)
        websocket.add_header(bytes("Authorization", "utf-8"), bytes("bearer " + self._wml_token, "utf-8"))

        print_text_header_h1("Metric monitor started for training run: " + str(run_uid))

        for event in websocket:
            if event.name == 'text':
                text = json.loads(event.text)
                status = text['status']
                if 'metrics' in status:
                    metrics = status['metrics']
                    if len(metrics) > 0:
                        metric = metrics[0]
                        values = ''
                        for x in metric['values']:
                            values = values + x['name'] + ':' + str(x['value']) + ' '

                        msg = metric['timestamp'] + ' ' + 'iteration:' + str(status['current_iteration']) + ' phase:' + metric['phase'] + ' ' + values
                        print(msg)

        print_text_header_h2("Metric monitor done.")

    def get_metrics(self, run_uid):
        """
             Get metrics values.

             :param run_uid: ID of trained model
             :type run_uid: str

             :returns: metric values
             :rtype: list

             A way you might use me is:

             >>> client.training.get_metrics(run_uid)
         """
        Training._validate_type(run_uid, 'run_uid', str, True)

        from lomond import WebSocket

        monitor_endpoint = self._wml_credentials['url'].replace('https',
                                                                'wss') + "/v3/models/" + run_uid + "/monitor"
        websocket = WebSocket(monitor_endpoint)
        websocket.add_header(bytes("Authorization", "utf-8"), bytes("bearer " + self._wml_token, "utf-8"))

        metric_list = []

        for event in websocket:
            if event.name == 'text':
                text = json.loads(event.text)
                status = text['status']
                if 'metrics' in status:
                    metrics = status['metrics']
                    if len(metrics) > 0:
                        metric = metrics[0]
                        metric_list.append(metric)

        return metric_list

    def _group_metrics(self, run_uid):
        metrics = self.get_metrics(run_uid)
        grouped_metrics = []

        if len(metrics) > 0:
            import collections
            grouped_metrics = collections.defaultdict(list)
            for d in metrics:
                k = d["phase"]
                grouped_metrics[k].append(d)

        return grouped_metrics

    def get_latest_metrics(self, run_uid):
        """
             Get latest metrics values.

             :param run_uid: ID of trained model
             :type run_uid: str

             :returns: metric values
             :rtype: list

             A way you might use me is:

             >>> client.training.get_latest_metrics(run_uid)
         """

        Training._validate_type(run_uid, 'run_uid', str, True)

        status = self.get_status(run_uid)
        latest_metrics = []

        if 'completed' in str(status):
            latest_metrics = status['metrics']
        else:
            grouped_metrics = self._group_metrics(run_uid)
            for key, value in grouped_metrics.items():
                sorted_value = sorted(value, key=lambda k: k['iteration'])
                latest_metrics.append(sorted_value[-1])

        return latest_metrics
