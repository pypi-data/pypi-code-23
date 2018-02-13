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
from watson_machine_learning_client.utils import get_headers, DEPLOYMENT_DETAILS_TYPE, print_text_header_h1, print_text_header_h2
from watson_machine_learning_client.wml_client_error import WMLClientError, MissingValue, ApiRequestFailure
from watson_machine_learning_client.href_definitions import is_uid
from watson_machine_learning_client.wml_resource import WMLResource


class Deployments(WMLResource):
    """
        Deploy and score published models.
    """
    def __init__(self, client, wml_credentials, wml_token, instance_details):
        WMLResource.__init__(self, __name__, client, wml_credentials, wml_token, instance_details)

    def _get_url_for_uid(self, deployment_uid):
        response_get = requests.get(
            self._href_definitions.get_deployments_href(),
            headers=get_headers(self._wml_token))

        try:
            if response_get.status_code == 200:
                for el in json.loads(response_get.text).get('resources'):
                    if el.get('metadata').get('guid') == deployment_uid:
                        return el.get('metadata').get('url')
            else:
                raise ApiRequestFailure('Couldn\'t generate url from uid: \'{}\'.'.format(deployment_uid), response_get)
        except Exception as e:
            raise WMLClientError('Failed during getting url for uid: \'{}\'.'.format(deployment_uid), e)

        raise WMLClientError('No matching url for uid: \'{}\'.'.format(deployment_uid))

    def get_details(self, deployment_uid=None):
        """
           Get information about your deployment(s).

           :param deployment_uid:  Deployment UID (optional)
           :type deployment_uid: str

           :returns: metadata of deployment(s)
           :rtype: dict

           A way you might use me is:

            >>> deployment_details = client.deployments.get_details(deployment_uid)
            >>> deployment_details = client.deployments.get_details(deployment_uid=deployment_uid)
            >>> deployments_details = client.deployments.get_details()
        """
        Deployments._validate_type(deployment_uid, 'deployment_uid', str, False)

        if deployment_uid is not None and not is_uid(deployment_uid):
            raise WMLClientError('\'deployment_uid\' is not an uid: \'{}\''.format(deployment_uid))

        if deployment_uid is not None:
            deployment_url = self._get_url_for_uid(deployment_uid)
        else:
            deployment_url = self._instance_details.get('entity').get('deployments').get('url')

        response_get = requests.get(
            deployment_url,
            headers=get_headers(self._wml_token))

        return self._handle_response(200, 'getting deployment(s) details', response_get)

    def create(self, model_uid, name, description='Model deployment', asynchronous=True):
        """
            Create model deployment (online).

            :param model_uid:  Published model UID
            :type model_uid: str
            :param name: Deployment name
            :type name: str
            :param description: Deployment description
            :type description: str
            :param asynchronous: if `False` then will wait until deployment will be fully created before returning
            :type asynchronous: bool

            :returns: details of created deployment
            :rtype: dict

            A way you might use me is:

             >>> deployment = client.deployments.create(model_uid, "Deployment X", "Online deployment of XYZ model.")
         """
        Deployments._validate_type(model_uid, 'model_uid', str, True)
        Deployments._validate_type(name, 'name', str, True)
        Deployments._validate_type(description, 'description', str, True)

        response_online = requests.post(
            self._instance_details.
            get('entity').
            get('published_models').
            get('url') + "/" + model_uid + "/" + "deployments",
            json={'name': name, 'description': description, 'type': 'online'},
            headers=get_headers(self._wml_token))

        if asynchronous:
            if response_online.status_code == 202:
                self._logger.warn('Deployment creation couldn\'t be finished in synchronous mode. Operation is continued in asynchronous mode. To monitor state of deployment use \'get_details()\' function.')
                return self._handle_response(202, 'deployment creation', response_online)
            else:
                return self._handle_response(201, 'deployment creation', response_online)
        else:
            deployment_details = json.loads(response_online.text)

            if response_online.status_code == 202:
                deployment_uid = self.get_uid(deployment_details)
                status = 'DEPLOY_IN_PROGRESS'

                def finished():
                    deployment_details = self._client.deployments.get_details(deployment_uid)
                    status = deployment_details['entity']['status']
                    print(status)
                    return status != 'DEPLOY_IN_PROGRESS'

                import time
                print_text_header_h1('Synchronous deployment creation for uid: \'{}\' started'.format(deployment_uid))
                while not finished():
                    time.sleep(5)

                if status == 'DEPLOY_SUCCESS':
                    print_text_header_h2("Successfully finished deployment creation, deployment_uid=\'{}\'".format(deployment_uid))
                    return deployment_details
                else:
                    print_text_header_h2("Deployment creation failed")
                    raise WMLClientError('Deployment creation failed.') # TODO - be more specific
            elif response_online.status_code == 201:
                deployment_uid = self.get_uid(deployment_details)
                print_text_header_h1('Synchronous deployment creation for uid: \'{}\' started'.format(deployment_uid))
                print_text_header_h2("Successfully finished deployment creation, deployment_uid=\'{}\'".format(deployment_uid))
                return deployment_details
            else:
                error_msg = "Deployment creation failed: {}".format(response_online.text)
                print_text_header_h2(error_msg)
                raise WMLClientError(error_msg)

    @staticmethod
    def get_scoring_url(deployment):
        """
            Get scoring_url from deployment details.

            :param deployment: Created deployment details
            :type deployment: dict

            :returns: scoring endpoint URL that is used for making scoring requests
            :rtype: str

            A way you might use me is:

             >>> scoring_endpoint = client.deployments.get_scoring_url(deployment)
        """
        Deployments._validate_type(deployment, 'deployment', dict, True)
        Deployments._validate_type_of_details(deployment, DEPLOYMENT_DETAILS_TYPE)

        try:
            url = deployment.get('entity').get('scoring_url')
        except Exception as e:
            raise WMLClientError('Getting scoring url for deployment failed.', e)

        if url is None:
            raise MissingValue('entity.scoring_url')

        return url

    @staticmethod
    def get_uid(deployment_details):
        """
            Get deployment_uid from deployment details.

            :param deployment_details: Created deployment details
            :type deployment_details: dict

            :returns: deployment UID that is used to manage the deployment
            :rtype: str

            A way you might use me is:

            >>> scoring_endpoint = client.deployments.get_deployment_uid(deployment)
        """
        Deployments._validate_type(deployment_details, 'deployment_details', dict, True)
        Deployments._validate_type_of_details(deployment_details, DEPLOYMENT_DETAILS_TYPE)

        try:
            uid = deployment_details.get('metadata').get('guid')
        except Exception as e:
            raise WMLClientError('Getting deployment uid from deployment details failed.', e)

        if uid is None:
            raise MissingValue('deployment_details.metadata.guid')

        return uid

    @staticmethod
    def get_url(deployment_details):
        """
            Get deployment_url from deployment details.

            :param deployment_details:  Created deployment details
            :type deployment_details: dict

            :returns: deployment URL that is used to manage the deployment
            :rtype: str

            A way you might use me is:

            >>> scoring_endpoint = client.deployments.get_deployment_url(deployment)
        """
        Deployments._validate_type(deployment_details, 'deployment_details', dict, True)
        Deployments._validate_type_of_details(deployment_details, DEPLOYMENT_DETAILS_TYPE)

        try:
            url = deployment_details.get('metadata').get('url')
        except Exception as e:
            raise WMLClientError('Getting deployment url from deployment details failed.', e)

        if url is None:
            raise MissingValue('deployment_details.metadata.url')

        return url

    def delete(self, deployment_uid):
        """
            Delete model deployment.

            :param deployment_uid: Deployment UID
            :type deployment_uid: str

            A way you might use me is:

            >>> client.deployments.delete(deployment_uid)
        """
        Deployments._validate_type(deployment_uid, 'deployment_uid', str, True)

        if deployment_uid is not None and not is_uid(deployment_uid):
            raise WMLClientError('\'deployment_uid\' is not an uid: \'{}\''.format(deployment_uid))

        deployment_url = self._get_url_for_uid(deployment_uid)

        response_delete = requests.delete(
            deployment_url,
            headers=get_headers(self._wml_token))

        self._handle_response(204, 'deployment deletion', response_delete, False)

    def score(self, scoring_url, payload):
        """
            Make scoring requests against deployed model.

            :param scoring_url:  scoring endpoint URL
            :type scoring_url: str
            :param payload: records to score
            :type payload: dict

            :returns: scoring result containing prediction and probability
            :rtype: dict

            A way you might use me is:

            >>> scoring_payload = {"fields": ["GENDER","AGE","MARITAL_STATUS","PROFESSION"], "values": [["M",23,"Single","Student"],["M",55,"Single","Executive"]]}
            >>> predictions = client.deployments.score(scoring_url, scoring_payload)
        """
        Deployments._validate_type(scoring_url, 'scoring_url', str, True)
        Deployments._validate_type(payload, 'payload', dict, True)

        response_scoring = requests.post(
            scoring_url,
            json=payload,
            headers=get_headers(self._wml_token))

        return self._handle_response(200, 'scoring', response_scoring)

    def list(self):
        """
           List deployments.

           A way you might use me is:

           >>> client.deployments.list()
        """
        from tabulate import tabulate

        details = self.get_details()
        resources = details['resources']
        values = [(m['metadata']['guid'], m['entity']['name'], m['entity']['type'], m['metadata']['created_at'], m['entity']['model_type']) for m in resources]
        table = tabulate([["GUID", "NAME", "TYPE", "CREATED", "FRAMEWORK"]] + values)
        print(table)
