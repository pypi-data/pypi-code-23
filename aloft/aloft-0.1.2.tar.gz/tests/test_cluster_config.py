import os
from aloft import cluster_config
from unittest import TestCase


class TestClusterConfig(TestCase):

    def test_should_get_cluster_config_values(self):
        os.environ['ALOFT_CONFIG'] = f'test-config'

        cluster_values = cluster_config.get_cluster_config_values('cl1.sandbox.test.com')

        expected_config_values = {
            'cluster': {
                'spec': {
                    'subnets': {
                        'privateSubnets':
                            [{'cidr': '10.10.0.0/25',
                              'zone': 'us-west-2a'},
                             {'cidr': '10.10.0.128/25',
                              'zone': 'us-west-2b'},
                             {'cidr': '10.10.1.0/25',
                              'zone': 'us-west-2c'}],
                        'publicSubnets':
                            [{'cidr': '10.10.1.128/27',
                              'zone': 'us-west-2a'},
                             {'cidr': '10.10.1.160/27',
                              'zone': 'us-west-2b'},
                             {'cidr': '10.10.1.192/27',
                              'zone': 'us-west-2c'}]}}},
            'masters': {
                'spec': {
                    'image': '099720109477/ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20171121.1',
                    'machineType': 't2.large',
                    'maxSize': 1,
                    'minSize': 1,
                    'zones': ['us-west-2a', 'us-west-2b', 'us-west-2c']}},
            'nodes': {
                'spec': {
                    'image': '099720109477/ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20171121.1',
                    'machineType': 'm4.large',
                    'maxSize': 4,
                    'minSize': 1,
                    'zones': ['us-west-2a', 'us-west-2b', 'us-west-2c']}}}
        self.assertEqual(expected_config_values, cluster_values)

    def test_should_get_cluster_config_filename(self):
        os.environ['ALOFT_CONFIG'] = f'test-config'

        filename = cluster_config.get_cluster_values_filename('cl1.sandbox.test.com')

        self.assertEqual('test-config/clusters/values/test.com/sandbox/cl1/cluster.yaml', filename)
