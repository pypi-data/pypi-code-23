from aloft import cluster
import os
from unittest import TestCase
from unittest.mock import call, patch


class TestCreateCluster(TestCase):

    @patch('aloft.cluster.get_or_create_vpc')
    @patch('aloft.cluster.execute')
    @patch('aloft.cluster.output.print_action')
    @patch('aloft.cluster.output.write_to_file')
    @patch('aloft.cluster.os.remove')
    @patch('aloft.cluster.aws.get_vpn_gateway_id')
    @patch('aloft.cluster.aws.get_route_table_ids')
    @patch('aloft.cluster.aws.propagate_route_table')
    @patch('aloft.cluster.aws.set_role_policy')
    @patch('aloft.cluster.time.sleep')
    @patch('aloft.cluster.aws.conditionally_create_hosted_zone_and_setup_ns_records')
    @patch('aloft.cluster.host.wait_for_domain_to_resolve')
    @patch('aloft.cluster.aws.get_or_create_s3_bucket')
    @patch.dict('aloft.cluster.os.environ', {'KUBECONFIG': 'TEST_ORIGINAL_KUBECONFIG'})
    def test_should_create_cluster(self,
                                   mock_get_or_create_s3_bucket,
                                   mock_wait_for_domain_to_resolve,
                                   mock_conditionally_create_hosted_zone_and_setup_ns_records,
                                   mock_sleep,
                                   mock_set_role_policy,
                                   mock_propagate_route_table,
                                   mock_get_route_table_ids,
                                   mock_get_vpn_gateway_id,
                                   mock_remove,
                                   mock_write_to_file,
                                   mock_print_action,
                                   mock_execute,
                                   mock_get_or_create_vpc):

        os.environ['ALOFT_CONFIG'] = f'test-config'
        mock_get_or_create_vpc.return_value = {'Name': 'sandbox', 'VpcId': 'TEST_AWS_VPC_ID'}
        mock_get_vpn_gateway_id.return_value = 'TEST_GATEWAY_ID'
        mock_get_route_table_ids.return_value = ['TEST_ROUTE_TABLE_ID_1', 'TEST_ROUTE_TABLE_ID_2']

        cluster.conditionally_create_vpc_and_cluster('cl1.sandbox.test.com')

        mock_get_or_create_vpc.assert_called_once_with('sandbox.test.com')
        mock_get_or_create_s3_bucket.assert_called_once_with('k8s-state.sandbox.test.com')
        mock_execute.assert_has_calls([
            call('kops toolbox template'
                 ' --values test-config/clusters/template/values.yaml'
                 ' --values test-config/clusters/values/test.com/sandbox/cl1/cluster.yaml'
                 ' --values test-config/clusters/values/test.com/sandbox/vpc.yaml'
                 ' --values /tmp/cl1.sandbox.test.com-dynamic.yaml'
                 ' --template test-config/clusters/template/template.yaml'
                 ' --format-yaml=true'
                 ' > /tmp/cl1.sandbox.test.com.yaml'),
            call('kops create -f /tmp/cl1.sandbox.test.com.yaml --state s3://k8s-state.sandbox.test.com'),
            call('ssh-keygen -q -f /tmp/cluster_rsa -t rsa -N ""'),
            call('kops create secret --name cl1.sandbox.test.com sshpublickey admin -i "/tmp/cluster_rsa.pub"'
                 ' --state s3://k8s-state.sandbox.test.com'),
            call('kops update cluster cl1.sandbox.test.com --yes --state s3://k8s-state.sandbox.test.com'),
            call('kops validate cluster cl1.sandbox.test.com --state s3://k8s-state.sandbox.test.com'),
            call('helm init'),
            call('kubectl rollout status -w deployment/tiller-deploy --namespace=kube-system')
        ])
        mock_write_to_file.assert_called_once_with(
            '/tmp/cl1.sandbox.test.com-dynamic.yaml',
            'networkId: TEST_AWS_VPC_ID\n'
            'clusterFQDN: cl1.sandbox.test.com\n'
            'kopsStateStore: s3://k8s-state.sandbox.test.com\n')
        mock_remove.assert_has_calls([
            call('/tmp/cluster_rsa'),
            call('/tmp/cluster_rsa.pub'),
            call('/tmp/cluster_rsa'),
            call('/tmp/cluster_rsa.pub')
        ])
        mock_propagate_route_table.assert_has_calls([
            call('TEST_ROUTE_TABLE_ID_1', 'TEST_GATEWAY_ID'),
            call('TEST_ROUTE_TABLE_ID_2', 'TEST_GATEWAY_ID')]
        )
        mock_set_role_policy.assert_called_once_with(
            'nodes.cl1.sandbox.test.com',
            'systemPolicy',
            '{\n  "Version": "2012-10-17",\n  "Statement": ["TEST_STATEMENT"]\n}'
        )

        mock_sleep.assert_called_once_with(300)
        mock_conditionally_create_hosted_zone_and_setup_ns_records.assert_called_once_with(
            'cl1.sandbox.test.com', 'sandbox.test.com'
        )
        mock_wait_for_domain_to_resolve.assert_called_once_with('cl1.sandbox.test.com')
        mock_print_action.assert_has_calls([
            call('Creating cluster cl1.sandbox.test.com in sandbox vpc.'),
            call('Waiting for cl1.sandbox.test.com to be ready.')
        ])


class TestDeleteCluster(TestCase):

    @patch('aloft.cluster.execute')
    @patch('aloft.cluster.aws.assume_role')
    def test_should_delete_cluster(self, mock_assume_role, mock_execute):
        cluster.delete_cluster('cl1.sandbox.test.com')

        mock_execute.assert_called_once_with(
            'kops delete cluster cl1.sandbox.test.com --yes --state s3://k8s-state.sandbox.test.com'
        )
        mock_assume_role.assert_called_once_with('sandbox')


class TestUseCluster(TestCase):

    @patch('aloft.cluster.execute')
    @patch('aloft.cluster.aws.assume_role')
    def test_should_use_cluster(self, mock_assume_role, mock_execute):
        cluster.use_cluster('cl1.sandbox.test.com')

        mock_execute.assert_called_once_with(
            'kops export kubecfg cl1.sandbox.test.com --state s3://k8s-state.sandbox.test.com'
        )
        mock_assume_role.assert_called_once_with('sandbox')


class TestGetClusters(TestCase):

    @patch('aloft.cluster.execute')
    @patch('aloft.cluster.print')
    @patch('aloft.cluster.aws.assume_role')
    def test_should_get_clusters_and_print_name_only(self, mock_assume_role, mock_print, mock_execute):
        os.environ['ALOFT_CONFIG'] = f'test-config'
        with open(f'test-data/kops-get-cluster-single-cluster.txt', 'r') as cluster_data_stream:
            mock_execute.return_value = cluster_data_stream.read()

        cluster.get_and_print_clusters('test.com', 'name')

        mock_assume_role.assert_called_once_with('sandbox')
        mock_execute.assert_called_once_with('kops get clusters -o yaml '
                                             '--state s3://k8s-state.sandbox.test.com', ['no clusters found'],
                                             quiet=True)
        mock_print.assert_has_calls([
            call('cl1.sandbox.test.com')
        ])

    @patch('aloft.cluster.execute')
    @patch('aloft.cluster.print')
    @patch('aloft.cluster.aws.assume_role')
    def test_should_get_clusters_and_print_name_only_for_multiple_clusters(self,
                                                                           mock_assume_role,
                                                                           mock_print,
                                                                           mock_execute):

        os.environ['ALOFT_CONFIG'] = f'test-config'
        with open(f'test-data/kops-get-cluster-multiple-clusters.txt', 'r') as cluster_data_stream:
            mock_execute.return_value = cluster_data_stream.read()

        cluster.get_and_print_clusters('test.com', 'name')

        mock_assume_role.assert_called_once_with('sandbox')
        mock_execute.assert_called_once_with(
            'kops get clusters -o yaml '
            '--state s3://k8s-state.sandbox.test.com', ['no clusters found'],
            quiet=True)
        mock_print.assert_has_calls([
            call('cl1.sandbox.test.com'),
            call('cl2.sandbox.test.com')
        ])

    @patch('aloft.cluster.execute')
    @patch('aloft.cluster.output.print_table')
    @patch('aloft.cluster.aws.assume_role')
    def test_should_get_clusters_and_print_text_for_multiple_clusters(self,
                                                                      mock_assume_role,
                                                                      mock_print_table,
                                                                      mock_execute):

        os.environ['ALOFT_CONFIG'] = f'test-config'
        with open(f'test-data/kops-get-cluster-multiple-clusters.txt', 'r') as cluster_data_stream:
            mock_execute.return_value = cluster_data_stream.read()

        cluster.get_and_print_clusters('test.com', 'text')

        mock_assume_role.assert_called_once_with('sandbox')
        mock_execute.assert_called_once_with(
            'kops get clusters -o yaml '
            '--state s3://k8s-state.sandbox.test.com', ['no clusters found'],
            quiet=True)
        mock_print_table.assert_has_calls([
            call(['NAME', 'VERSION', 'CIDR'], [
                ['cl1.sandbox.test.com', '1.9.1', '10.10.0.0/21'],
                ['cl2.sandbox.test.com', '1.8.5', '10.10.2.0/21']
            ], '{0: <40} {1: <10} {2: <18}')
        ])

    @patch('aloft.cluster.execute')
    @patch('aloft.cluster.output.print_list_as_yaml')
    @patch('aloft.cluster.aws.assume_role')
    def test_should_get_clusters_and_print_yaml_for_multiple_clusters(self,
                                                                      mock_assume_role,
                                                                      mock_print_list_as_yaml,
                                                                      mock_execute):

        os.environ['ALOFT_CONFIG'] = f'test-config'
        with open(f'test-data/kops-get-cluster-multiple-clusters.txt', 'r') as cluster_data_stream:
            mock_execute.return_value = cluster_data_stream.read()

        cluster.get_and_print_clusters('test.com', 'yaml')

        mock_assume_role.assert_called_once_with('sandbox')
        mock_execute.assert_called_once_with(
            'kops get clusters -o yaml '
            '--state s3://k8s-state.sandbox.test.com', ['no clusters found'],
            quiet=True)
        self.assertEqual(2, len(mock_print_list_as_yaml.call_args[0][0]))
        self.assertEqual('cl1.sandbox.test.com', mock_print_list_as_yaml.call_args[0][0][0]['metadata']['name'])
        self.assertEqual('cl2.sandbox.test.com', mock_print_list_as_yaml.call_args[0][0][1]['metadata']['name'])


class TestGetCurrentCluster(TestCase):

    @patch('aloft.cluster.execute')
    @patch('aloft.cluster.print')
    @patch('aloft.cluster.aws.assume_role')
    def test_should_get_current_cluster_and_print_name_only(self, mock_assume_role, mock_print, mock_execute):
        os.environ['ALOFT_CONFIG'] = f'test-config'
        with open(f'test-data/kops-get-cluster-multiple-clusters.txt', 'r') as cluster_data_stream:
            mock_execute.side_effect = ['cl2.sandbox.test.com\n', cluster_data_stream.read()]

        cluster.get_and_print_current_cluster('name')

        mock_assume_role.assert_called_once_with('sandbox')
        mock_execute.assert_has_calls([
            call('kubectl config current-context', quiet=True),
            call('kops get clusters -o yaml '
                 '--state s3://k8s-state.sandbox.test.com', ['no clusters found'],
                 quiet=True)
        ])
        mock_print.assert_has_calls([
            call('cl2.sandbox.test.com')
        ])

    @patch('aloft.cluster.execute')
    @patch('aloft.cluster.output.print_table')
    @patch('aloft.cluster.aws.assume_role')
    def test_should_get_current_cluster_and_print_text(self, mock_assume_role, mock_print_table, mock_execute):
        os.environ['ALOFT_CONFIG'] = f'test-config'
        with open(f'test-data/kops-get-cluster-multiple-clusters.txt', 'r') as cluster_data_stream:
            mock_execute.side_effect = ['cl2.sandbox.test.com\n', cluster_data_stream.read()]

        cluster.get_and_print_current_cluster('text')

        mock_assume_role.assert_called_once_with('sandbox')
        mock_execute.assert_has_calls([
            call('kubectl config current-context', quiet=True),
            call('kops get clusters -o yaml '
                 '--state s3://k8s-state.sandbox.test.com', ['no clusters found'],
                 quiet=True)
        ])
        mock_print_table.assert_has_calls([
            call(['NAME', 'VERSION', 'CIDR'], [
                ['cl2.sandbox.test.com', '1.8.5', '10.10.2.0/21']
            ], '{0: <40} {1: <10} {2: <18}')
        ])

    @patch('aloft.cluster.execute')
    @patch('aloft.cluster.output.print_list_as_yaml')
    @patch('aloft.cluster.aws.assume_role')
    def test_should_get_current_cluster_and_print_yaml(self,
                                                       mock_assume_role,
                                                       mock_print_list_as_yaml,
                                                       mock_execute):

        os.environ['ALOFT_CONFIG'] = f'test-config'
        with open(f'test-data/kops-get-cluster-multiple-clusters.txt', 'r') as cluster_data_stream:
            mock_execute.side_effect = ['cl2.sandbox.test.com\n', cluster_data_stream.read()]

        cluster.get_and_print_current_cluster('yaml')

        mock_assume_role.assert_called_once_with('sandbox')
        mock_execute.assert_has_calls([
            call('kubectl config current-context', quiet=True),
            call('kops get clusters -o yaml '
                 '--state s3://k8s-state.sandbox.test.com', ['no clusters found'],
                 quiet=True)
        ])
        self.assertEqual(1, len(mock_print_list_as_yaml.call_args[0][0]))
        self.assertEqual('cl2.sandbox.test.com', mock_print_list_as_yaml.call_args[0][0][0]['metadata']['name'])
