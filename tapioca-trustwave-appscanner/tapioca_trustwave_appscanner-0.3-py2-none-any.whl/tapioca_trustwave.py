# coding: utf-8
import os

from tapioca import (
    TapiocaAdapter, generate_wrapper_from_adapter, JSONAdapterMixin)

from .resource_mapping import RESOURCE_MAPPING


class TrustwaveClientAdapter(JSONAdapterMixin, TapiocaAdapter):
    resource_mapping = RESOURCE_MAPPING

    def get_api_root(self, api_params):
        return os.getenv('TRUSTWAVE_API_ROOT')

    def get_request_kwargs(self, api_params, *args, **kwargs):
        params = super(TrustwaveClientAdapter, self).get_request_kwargs(
            api_params, *args, **kwargs)
        return params

    def get_iterator_list(self, response_data):
        return response_data

    def get_iterator_next_request_kwargs(self, iterator_request_kwargs,
                                         response_data, response):
        pass


Trustwave = generate_wrapper_from_adapter(TrustwaveClientAdapter)
