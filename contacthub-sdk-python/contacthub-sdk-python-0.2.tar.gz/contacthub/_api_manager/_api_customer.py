# -*- coding: utf-8 -*-
import requests
import json

from copy import deepcopy
from requests import HTTPError

from contacthub.errors.api_error import APIError
from contacthub.lib.utils import DateEncoder


class _CustomerAPIManager(object):
    """
    A wrapper for Contacthub API.
    This is the lowest level for accessing the customer API, use this class for get, put, patch or post data on customer
    entity.
    """

    def __init__(self, node):
        """
        :param node: the Node object for retrieving customers data
        """
        self.node = node
        self.request_url = self.node.workspace.base_url + '/' + self.node.workspace.workspace_id + '/customers'
        self.headers = {'Authorization': 'Bearer ' + self.node.workspace.token, 'Content-Type': 'application/json'}

    def get_all(self, externalId=None, fields=None, query=None, size=None, page=None):
        # type: (str, list, dict, int, int) -> dict
        """
        Get all customer in the specified Node.

        :rtype: dict
        :param externalId: The external id assigned to the customers
        :param fields: Comma-separated list of properties to include in the response
        :param query: a dictionary query for filter the customers
        :param size: the size of the pages containing customers
        :param page: the number of the page for retrieve customer's data
        :return: A dictionary representing the JSON response from the API called if there were no errors, else raise an
            HTTPException
        """
        params = {'nodeId': self.node.node_id}
        if query:
            params['query'] = json.dumps(query, cls=DateEncoder)
        if externalId:
            params['externalId'] = str(externalId)
        if size:
            params['size'] = size
        if page:
            params['page'] = page
        if fields:
            params['fields'] = ",".join(fields)
        resp = requests.get(self.request_url, params=params, headers=self.headers)
        response_text = json.loads(resp.text)
        if 200 <= resp.status_code < 300:
            return response_text
        raise APIError("Status code: %s. Message: %s. Errors: %s. Data: %s. Logref: %s" % (resp.status_code,
                                                                                           response_text['message'],
                                                                                           response_text['errors'],
                                                                                           response_text['data'],
                                                                                           response_text['logref']))

    def get(self, _id, urls_extra=None):
        """
        Get a customer in the specified Node.

        :param _id: the id of the customer to get
        :param urls_extra: The extra url at the end of the base url of this class, for reaching end point of other
            entities like Job, Education and Like
        :return: A dictionary representing the JSON response from the API called if there were no errors, else raise an
            HTTPException
        """
        request_url = self.request_url + '/' + str(_id)
        if urls_extra:
            request_url += "/" + urls_extra
        resp = requests.get(request_url, headers=self.headers)
        response_text = json.loads(resp.text)
        if 200 <= resp.status_code < 300:
            return response_text
        raise APIError("Status code: %s. Message: %s. Errors: %s. Data: %s. Logref: %s" % (resp.status_code,
                                                                                           response_text['message'],
                                                                                           response_text['errors'],
                                                                                           response_text['data'],
                                                                                           response_text['logref']))

    def post(self, body, urls_extra=None, force_update=False):
        """
        POST a new customer in the specified Node.
        If urls_extra is specified, post the new entity related to customer, like Job, Education and Like
        If the status code of the response is 409 (CONFLICT) and the parameter force_update is true,
        redirect the body to a PATCH request.

        :param force_update: if True and the customer already exists in CH, this method redirect the body to a PATCH
            request.
        :param urls_extra: The extra url at the end of the base url of this class, for reaching end point of other
            entities like Job, Education and Like
        :param body: the body of the POST request containing the new Customers data
        :return: A dictionary representing the JSON response from the API called if there were no errors, else raise an
            HTTPException
        """
        if not urls_extra:
            body['nodeId'] = self.node.node_id
            request_url = self.request_url
        else:
            request_url = self.request_url + "/" + urls_extra
        body = json.loads(json.dumps(body, cls=DateEncoder))
        resp = requests.post(request_url, json=body, headers=self.headers)
        response_text = json.loads(resp.text)
        if 200 <= resp.status_code < 300:
            return response_text
        if resp.status_code == 409 and force_update:
            body.pop('nodeId', None)
            return self.patch(_id=response_text['data']['customer']['id'], body=body)
        raise APIError("Status code: %s. Message: %s. Errors: %s. Data: %s. Logref: %s" % (resp.status_code,
                                                                                           response_text['message'],
                                                                                           response_text['errors'],
                                                                                           response_text['data'],
                                                                                           response_text['logref']))

    def delete(self, _id, urls_extra=None):
        """
        Delete a customer in the specified Node. If urls_extra is specified, delete the entity related to Customer,
        like Job, Education and Like

        :param _id: the id of the customer to delete or the entity related to customer, like Job, Education and Like
        :return: A dictionary representing the JSON response from the API called if there were no errors, else raise an
            HTTPException
        """
        request_url = self.request_url + '/' + str(_id)
        if urls_extra:
            request_url += '/' + urls_extra
        resp = requests.delete(request_url, headers=self.headers)
        if resp.text:
            response_text = json.loads(resp.text)
        else:
            response_text = resp.text
        if 200 <= resp.status_code < 300:
            return response_text
        raise APIError("Status code: %s. Message: %s. Errors: %s. Data: %s. Logref: %s" % (resp.status_code,
                                                                                           response_text['message'],
                                                                                           response_text['errors'],
                                                                                           response_text['data'],
                                                                                           response_text['logref']))

    def patch(self, _id, body):
        """
        Execute a PATCH request on a customer in the specified Node.

        :param _id: the id of the customer to patch
        :param body: a dictionary containing the body of the PATCH request
        :return: A dictionary representing the JSON response from the API called if there were no errors, else raise an
            HTTPException
        """

        body = json.dumps(body, cls=DateEncoder)
        resp = requests.patch(self.request_url + '/' + str(_id), json=json.loads(body), headers=self.headers)
        response_text = json.loads(resp.text)
        if 200 <= resp.status_code < 300:
            return response_text
        raise APIError("Status code: %s. Message: %s. Errors: %s. Data: %s. Logref: %s" % (resp.status_code,
                                                                                           response_text['message'],
                                                                                           response_text['errors'],
                                                                                           response_text['data'],
                                                                                           response_text['logref']))

    def put(self, _id, body, urls_extra=None):
        """
        Execute a PUT request on a customer in the specified Node. If urls_extra is specified, PUT the entity related to
        Customer, like Job, Education and Like

        :param _id: the id of the customer to put
        :param body: a dictionary containing the body of the PUT request
        :return: A dictionary representing the JSON response from the API called if there were no errors, else raise an
            HTTPException
        """
        request_url = self.request_url + '/' + str(_id)
        if urls_extra:
            request_url += '/' + urls_extra
        body = json.loads(json.dumps(body, cls=DateEncoder))
        resp = requests.put(request_url, json=body, headers=self.headers)
        response_text = json.loads(resp.text)
        if 200 <= resp.status_code < 300:
            return response_text
        raise APIError("Status code: %s. Message: %s. Errors: %s. Data: %s. Logref: %s" % (resp.status_code,
                                                                                           response_text['message'],
                                                                                           response_text['errors'],
                                                                                           response_text['data'],
                                                                                           response_text['logref']))
