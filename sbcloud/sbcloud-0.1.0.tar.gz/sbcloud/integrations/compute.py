import copy
import json

import libcloud

from sbcloud import BaseCloudIntegration


class _IgnoreInvalidEncoder(json.JSONEncoder):
    """JSON encoder defaulting to stringifying any objects not supporting default JSON serialization"""
    def default(self, o):
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return str(o)


class BaseComputeIntegration(BaseCloudIntegration):
    """Base class for all COMPUTE driver integrations"""

    driver_type = libcloud.DriverType.COMPUTE


class ComputeListNodesIntegration(BaseComputeIntegration):
    """List Nodes"""

    def execute(self):
        return [self.marshal_node_format(node) for node in self.driver.list_nodes()]

    def marshal_node_format(self, node):
        """Convert result data to manifest output format"""
        data = copy.copy(node.__dict__)

        # Remove empty _uuid node key carried over from __dict__
        del data['_uuid']

        # Remove driver instance from results
        data.pop('driver', None)

        # CSV IP lists, replacing None with empty strings
        for key in ('private_ips', 'public_ips'):
            data[key] = ','.join([ip or '' for ip in data[key]])

        # Stringify extra JSON data, stringifying any complex objects
        data['extra'] = json.dumps(data.get('extra', {}), indent=4, cls=_IgnoreInvalidEncoder)

        return data
