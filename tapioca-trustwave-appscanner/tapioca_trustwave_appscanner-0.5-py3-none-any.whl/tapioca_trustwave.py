# coding: utf-8

from tapioca import (
    TapiocaAdapter, generate_wrapper_from_adapter, JSONAdapterMixin)

from .resource_mapping import RESOURCE_MAPPING


class TrustwaveClientAdapter(JSONAdapterMixin, TapiocaAdapter):
    api_root = '{protocol}://{server}/Hailstorm.WS/HailstormRESTService.svc/client/{client}/customer/{customer}/'
    resource_mapping = RESOURCE_MAPPING

    def get_api_root(self, api_params):
        protocol = api_params.get('protocol', 'https')  # default https
        server = api_params.get('server')
        client = api_params.get('client')
        customer = api_params.get('customer')
        return self.api_root.format(protocol=protocol, server=server, client=client, customer=customer)

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
