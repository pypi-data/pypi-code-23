import copy

import libcloud

from sbcloud import BaseCloudIntegration
from sbcloud.util import safe_json_dumps


class BaseComputeIntegration(BaseCloudIntegration):
    """Base class for all libcloud COMPUTE driver integrations

    Provides several hooks to allow overriding non-standard libcloud driver functions / signatures
    """

    driver_type = libcloud.DriverType.COMPUTE

    # Potential start_node function names, varies by driver
    __start_node_funcs = [
        'ex_start_node',
        'ex_power_on_node'
    ]
    # Potential stop_node function names, varies by driver
    __stop_node_funcs = [
        'ex_stop_node',
        'ex_shutdown_node',
    ]

    def get_node(self, node_id):
        """Return libcloud Node instance or raise ValueError if not found"""
        nodes = {node.id: node for node in self.list_nodes()}

        try:
            return nodes[node_id]
        except KeyError:
            raise ValueError('No node with id "{}" found'.format(node_id))

    def list_nodes(self):
        """Return list of all libcloud Node instances"""
        return self.driver.list_nodes()

    def start_node(self, node):
        """Start a libcloud Node"""
        for func_name in self.__start_node_funcs:
            func = getattr(self.driver, func_name, None)
            if func:
                return func(node)
        else:
            raise NotImplementedError('Driver "{}" does not support starting nodes'.format(self.provider))

    def stop_node(self, node):
        """Stop a libcloud Node"""
        for func_name in self.__stop_node_funcs:
            func = getattr(self.driver, func_name, None)
            if func:
                return func(node)
        else:
            raise NotImplementedError('Driver "{}" does not support stopping nodes'.format(self.provider))

    def reboot_node(self, node):
        """Reboot a libcloud Node"""
        return self.driver.reboot_node(node)

    def destroy_node(self, node):
        """Destroy a libcloud Node"""
        return self.driver.destroy_node(node)

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
        data['extra'] = safe_json_dumps(data.get('extra'))

        return data


class ComputeListNodesIntegration(BaseComputeIntegration):
    """List Nodes"""

    def execute(self):
        return [self.marshal_node_format(node) for node in self.list_nodes()]


class ComputeStartNodeIntegration(BaseComputeIntegration):
    """Start Node"""

    def execute(self):
        node = self.get_node(self.inputs['node_id'])
        previous_state = node.state

        self.start_node(node)

        return {'previous_state': previous_state}


class ComputeStopNodeIntegration(BaseComputeIntegration):
    """Stop Node"""

    def execute(self):
        node = self.get_node(self.inputs['node_id'])
        previous_state = node.state

        self.stop_node(node)

        return {'previous_state': previous_state}
