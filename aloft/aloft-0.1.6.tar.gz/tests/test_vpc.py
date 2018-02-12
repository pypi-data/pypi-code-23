import os
from aloft.vpc import get_vpc, get_or_create_vpc, delete_vpc
from unittest import TestCase
from unittest.mock import patch


class TestGetVpc(TestCase):

    @patch('aloft.vpc.aws.get_vpc_by_name')
    def test_should_get_vpc(self, mock_get_vpc_by_name):
        mock_get_vpc_by_name.return_value = {'Name': 'sandbox'}

        vpc = get_vpc('sandbox.test.com')

        self.assertEqual({'Name': 'sandbox'}, vpc)


class TestCreateVpc(TestCase):

    @patch('aloft.vpc.aws.get_vpc_by_name')
    def test_should_return_vpc_if_exists(self, mock_get_vpc_by_name):
        mock_get_vpc_by_name.return_value = {'Name': 'sandbox'}

        vpc = get_or_create_vpc('sandbox.test.com')

        self.assertEqual({'Name': 'sandbox'}, vpc)

    @patch('aloft.vpc.aws.get_vpc_by_name')
    @patch('aloft.vpc.aws.create_vpc')
    @patch('aloft.vpc.aws.create_and_attach_internet_gateway')
    @patch('aloft.vpc.aws.create_and_attach_vpn_gateway')
    def test_should_create_vpc_if_not_exists(self,
                                             mock_create_and_attach_vpn_gateway,
                                             mock_create_and_attach_internet_gateway,
                                             mock_create_vpc,
                                             mock_get_vpc_by_name):
        os.environ['ALOFT_CONFIG'] = f'test-config'
        mock_get_vpc_by_name.return_value = None
        mock_create_vpc.return_value = {'Name': 'sandbox'}

        vpc = get_or_create_vpc('sandbox.test.com')

        self.assertEqual({'Name': 'sandbox'}, vpc)
        mock_create_vpc.assert_called_once_with('sandbox', '10.10.0.0/21')
        mock_create_and_attach_internet_gateway.assert_called_once_with({'Name': 'sandbox'})
        mock_create_and_attach_vpn_gateway.assert_called_once_with({'Name': 'sandbox'})


class TestDeleteVpc(TestCase):

    @patch('aloft.vpc.aws.delete_network_and_vpc')
    def test_should_delete_vpc(self, mock_delete_network_and_vpc):
        delete_vpc('sandbox.test.com')

        mock_delete_network_and_vpc.assert_called_once_with('sandbox')
