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

    def get_node(self, node_id):
        """Return libcloud Node instance or raise ValueError if not found"""
        nodes = {node.id: node for node in self.driver.list_nodes()}

        try:
            return nodes[node_id]
        except KeyError:
            raise ValueError('No node with id "{}" found'.format(node_id))


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


class ComputeStartNodeIntegration(BaseComputeIntegration):
    """Start Node"""

    def execute(self):
        node = self.get_node(self.inputs['node_id'])
        previous_state = node.state

        self.driver.ex_start_node(node)

        return {'previous_state': previous_state}


class ComputeStopNodeIntegration(BaseComputeIntegration):
    """Stop Node"""

    def execute(self):
        node = self.get_node(self.inputs['node_id'])
        previous_state = node.state

        self.driver.ex_stop_node(node)

        return {'previous_state': previous_state}
