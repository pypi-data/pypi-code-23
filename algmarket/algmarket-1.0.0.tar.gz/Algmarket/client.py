'Algorithmia API Client (python)'

import Algmarket
from Algmarket.algorithm import Algorithm
from Algmarket.datafile import DataFile
from Algmarket.datadirectory import DataDirectory

import json, re, requests, six
import os

class Client(object):
    'Algorithmia Common Library'

    apiKey = None
    apiAddress = None

    def __init__(self, apiKey = None, apiAddress = None):
        # Override apiKey with environment variable
        if apiKey is None and 'ALGMARKET_KEY' in os.environ:
            apiKey = os.environ['ALGMARKET_KEY']
        self.apiKey = apiKey
        if apiAddress is not None:
            self.apiAddress = apiAddress
        else:
            self.apiAddress = Algmarket.getApiAddress()

    def algm(self, algmRef):
        return Algorithm(self, algmRef)

    def file(self, dataUrl):
        return DataFile(self, dataUrl)

    def dir(self, dataUrl):
        return DataDirectory(self, dataUrl)

    # Used internally to post json to the api and parse json response
    def postJsonHelper(self, url, input_object, parse_response_as_json=True, **query_parameters):
        headers = {}
        if self.apiKey is not None:
            headers['KeyValue'] = self.apiKey

        input_json = None
        if input_object is None:
            input_json = json.dumps(None).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        elif isinstance(input_object, six.string_types):
            input_json = input_object.encode('utf-8')
            headers['Content-Type'] = 'text/plain'
        elif isinstance(input_object, bytearray) or isinstance(input_object, bytes):
            input_json = bytes(input_object)
            headers['Content-Type'] = 'application/octet-stream'
        else:
            input_json = json.dumps(input_object).encode('utf-8')
            headers['Content-Type'] = 'application/json'

        response = requests.post(self.apiAddress + url, data=input_json, headers=headers, params=query_parameters)

        if parse_response_as_json:
            return response.json()
        return response

    # Used internally to http get a file
    def getHelper(self, url, **query_parameters):
        headers = {}
        if self.apiKey is not None:
            headers['KeyValue'] = self.apiKey
        return requests.get(self.apiAddress + url, headers=headers, params=query_parameters)

    def patchHelper(self, url, params):
        headers = {'content-type': 'application/json'}
        if self.apiKey is not None:
            headers['KeyValue'] = self.apiKey
        return requests.patch(self.apiAddress + url, headers=headers, data=json.dumps(params))

    # Used internally to get http head result
    def headHelper(self, url):
        headers = {}
        if self.apiKey is not None:
            headers['KeyValue'] = self.apiKey
        return requests.head(self.apiAddress + url, headers=headers)

    # Used internally to http put a file
    def putHelper(self, url, data):
        headers = {}
        if self.apiKey is not None:
            headers['KeyValue'] = self.apiKey
        response = requests.put(self.apiAddress + url, data=data, headers=headers)
        return response.json()

    # Used internally to http delete a file
    def deleteHelper(self, url):
        headers = {}
        if self.apiKey is not None:
            headers['KeyValue'] = self.apiKey
        response = requests.delete(self.apiAddress + url, headers=headers)
        return response.json()
