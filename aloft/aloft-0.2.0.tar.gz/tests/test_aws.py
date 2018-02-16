from aloft import aws
from unittest import TestCase
from unittest.mock import Mock, patch


class TestVpc(TestCase):

    @patch('aloft.aws.boto3.client')
    def test_should_get_vpc(self, mock_client):
        aws.credentials = {
            'AccessKeyId': 'TEST_ACCESS_KEY_ID',
            'SecretAccessKey': 'TEST_SECRET_ACCESS_KEY',
            'SessionToken': 'TEST_SESSION_TOKEN'
        }
        mock_ec2 = Mock()
        mock_ec2.describe_vpcs = Mock()
        mock_client.return_value = mock_ec2
        mock_ec2.describe_vpcs.return_value = {
            'Vpcs': [
                {
                    'CidrBlock': '10.10.0.0/21',
                    'DhcpOptionsId': 'dopt-c62433a1',
                    'State': 'available',
                    'VpcId': 'vpc-9669a4ef',
                    'InstanceTenancy': 'default',
                    'CidrBlockAssociationSet': [{
                        'AssociationId': 'vpc-cidr-assoc-8a7ef0e1',
                        'CidrBlock': '10.10.0.0/21',
                        'CidrBlockState': {'State': 'associated'}}],
                    'IsDefault': False,
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'sandbox'
                        },
                        {
                            'Key': 'kubernetes.io/cluster/cl1.sandbox.test.com',
                            'Value': 'shared'
                        },
                        {
                            'Key': 'kubernetes.io/cluster/cl2.sandbox.test.com',
                            'Value': 'shared'
                        },
                        {
                            'Key': 'kubernetes.io/cluster/cl3.sandbox.test.com',
                            'Value': 'shared'
                        },
                        {
                            'Key': 'kubernetes.io/cluster/cl4.sandbox.test.com',
                            'Value': 'shared'
                        }
                    ]
                }
            ]
        }

        vpc = aws.get_vpc_by_name('sandbox')

        self.assertEqual(mock_ec2.describe_vpcs.return_value['Vpcs'][0], vpc)
