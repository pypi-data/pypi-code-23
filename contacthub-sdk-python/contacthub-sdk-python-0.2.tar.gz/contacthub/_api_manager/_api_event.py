# -*- coding: utf-8 -*-
import json
from datetime import datetime
import requests
from contacthub.lib.utils import DateEncoder
from requests import HTTPError

from contacthub.errors.api_error import APIError


class _EventAPIManager(object):
    """
    A wrapper for Contacthub API.
    This is the lowest level for accessing the event API, use this class for get, put, patch or post data on event
    entity.
    """

    def __init__(self, node):
        """
        :param node: the Node object for retrieving Events data
        """
        self.node = node
        self.request_url = self.node.workspace.base_url + '/' + self.node.workspace.workspace_id + '/events'
        self.headers = {'Authorization': 'Bearer ' + self.node.workspace.token, 'Content-Type': 'application/json'}

    def get_all(self, customer_id, type=None, context=None, mode=None, dateFrom=None, dateTo=None, page=None,
                size=None):
        """
        Retrieve all the events of the associated Node from the API.

        :param customer_id: The id of the customer owner of the event
        :param type: the type of the event present in Event.TYPES
        :param context: the context of the event present in Event.CONTEXT
        :param mode: the mode of event. ACTIVE if the customer made the event, PASSIVE if the customer recive the event
        :param dateFrom: From string or datetime for search of event
        :param dateTo: From string or datetime for search of event
        :param size: the size of the pages containing customers
        :param page: the number of the page for retrieve customer's data
        :return: A dictionary representing the JSON response from the API called if there were no errors, else raise an
            HTTPException
       """
        params = {'customerId': customer_id}
        if type:
            params['type'] = type
        if context:
            params['context'] = context
        if mode:
            params['mode'] = mode
        if dateFrom:
            if isinstance(dateFrom, datetime):
                date_from = dateFrom.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                date_from = dateFrom
            params['dateFrom'] = date_from
        if dateTo:
            if isinstance(dateTo, datetime):
                date_to = dateTo.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                date_to = dateTo
            params['dateTo'] = date_to
        if page:
            params['page'] = page
        if size:
            params['size'] = size
        resp = requests.get(self.request_url, params=params, headers=self.headers)
        response_text = json.loads(resp.text)
        if 200 <= resp.status_code < 300:
            return response_text
        raise APIError("Status code: %s. Message: %s. Errors: %s. Data: %s. Logref: %s" % (resp.status_code,
                                                                                           response_text['message'],
                                                                                           response_text['errors'],
                                                                                           response_text['data'],
                                                                                           response_text['logref']))

    def get(self, _id):
        """
        Get the event associated to the given id

        :param _id: the id of the event to get
        :return: A dictionary representing the JSON response from the API called if there were no errors, else raise an
            HTTPException
        """
        resp = requests.get(self.request_url + '/' + _id, headers=self.headers)
        response_text = json.loads(resp.text)
        if 200 <= resp.status_code < 300:
            return response_text
        raise APIError("Status code: %s. Message: %s. Errors: %s. Data: %s. Logref: %s" % (resp.status_code,
                                                                                           response_text['message'],
                                                                                           response_text['errors'],
                                                                                           response_text['data'],
                                                                                           response_text['logref']))

    def post(self, body):
        """
        Post a new event with the given body

        :param body: the body of the POST request containing the new Customers data
        :return: A dictionary representing the JSON response from the API called if there were no errors, else raise an
            HTTPException
        """
        body = json.dumps(body, cls=DateEncoder)
        resp = requests.post(self.request_url, headers=self.headers, json=json.loads(body))
        if resp.text:
            response_text = json.loads(resp.text)
            if 200 <= resp.status_code < 300:
                return response_text
            raise APIError("Status code: %s. Message: %s. Errors: %s. Data: %s. Logref: %s" % (resp.status_code,
                                                                                           response_text['message'],
                                                                                           response_text['errors'],
                                                                                           response_text['data'],
                                                                                           response_text['logref']))
