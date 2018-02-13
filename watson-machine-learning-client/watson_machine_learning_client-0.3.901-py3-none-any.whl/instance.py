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
from watson_machine_learning_client.utils import get_headers
from watson_machine_learning_client.wml_client_error import NoWMLCredentialsProvided, MissingValue, ApiRequestFailure


class ServiceInstance:
    """
        Connect, get details and check usage of your Watson Machine Learning service instance.
    """
    def __init__(self, wml_credentials, wml_token):
        if wml_credentials is None:
            raise NoWMLCredentialsProvided
        if wml_token is None:
            raise MissingValue('wml_token')
        self.wml_credentials = wml_credentials
        self.wml_token = wml_token

    def get_details(self):
        """
             Get information about our instance of Watson Machine Learning service.

             :returns: metadata of service instance
             :rtype: dict

             A way you might use me is:

             >>> instance_details = client.service_instance.get_details()
        """
        if self.wml_credentials is not None:
            response_get_instance = requests.get(
                self.wml_credentials['url'] + "/v3/wml_instances/"
                + self.wml_credentials['instance_id'],
                headers=get_headers(self.wml_token))

            if response_get_instance.status_code == 200:
                return json.loads(response_get_instance.text)
            else:
                raise ApiRequestFailure('Getting instance details failed.', response_get_instance)
        else:
            raise NoWMLCredentialsProvided
