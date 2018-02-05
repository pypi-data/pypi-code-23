#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose:
        Swagger Codegen API Methods
'''

__author__ = 'Matt Joyce'
__email__ = 'matt@joyce.nyc'
__copyright__ = 'Copyright 2016, Symphony Communication Services LLC'


import logging
import pkg_resources

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient
from bravado.swagger_model import load_file


class SymCodegen():

    def __init__(self, logger=None):
        self.agent_swagger = pkg_resources.resource_filename('symphonybinding', 'data/agent-api-public-deprecated.yaml')
        self.pod_swagger = pkg_resources.resource_filename('symphonybinding', 'data/pod-api-public-deprecated.yaml')
        self.logger = logger or logging.getLogger(__name__)

    def agent_cg(self, url):
        http_client = RequestsClient()
        self.__url__ = url
        assert http_client
        # load deprecated agent codegen objects from spec
        try:
            agent = SwaggerClient.from_spec(load_file(self.agent_swagger),
                                            config={'also_return_response': True})
            agent.swagger_spec.api_url = self.__url__
        except Exception as err:
            self.logger.error(err)
        return agent

    def pod_cg(self, url):
        http_client = RequestsClient()
        self.__url__ = url
        assert http_client
        # load deprecated agent codegen objects from spec
        try:
            pod = SwaggerClient.from_spec(load_file(self.pod_swagger),
                                          config={'also_return_response': True})
            pod.swagger_spec.api_url = self.__url__
        except Exception as err:
            self.logger.error(err)
        return pod
