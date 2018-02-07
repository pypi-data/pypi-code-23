import os
from aloft import volume
from unittest import TestCase
from unittest.mock import call, patch


class TestLockVolumes(TestCase):

    @patch('aloft.volume.k8s.get_resources')
    @patch('aloft.volume.k8s.get_resource_by_name')
    @patch('aloft.volume.aws.delete_ec2_tags')
    @patch('aloft.volume.aws.create_ec2_tags')
    @patch('aloft.volume.aws.save_content_to_s3')
    @patch('aloft.volume.output.print_action')
    @patch('aloft.volume.output.print_details')
    def test_should_lock_volumes(self,
                                 mock_print_details,
                                 mock_print_action,
                                 mock_save_content_to_s3,
                                 mock_create_ec2_tags,
                                 mock_delete_ec2_tags,
                                 mock_get_resource_by_name,
                                 mock_get_resources):

        os.environ['ALOFT_CONFIG'] = f'test-config'
        mock_get_resources.return_value = [{'spec': {'volumeName': 'TEST_VOLUME_ID_NAME_1'}}]
        mock_get_resource_by_name.return_value = {
            'apiVersion': 'TEST_API_VERSION',
            'kind': 'PersistentVolume',
            'metadata': {'name': 'TEST_VOLUME_ID_NAME'},
            'spec': {
                'persistentVolumeReclaimPolicy': 'Delete',
                'awsElasticBlockStore': {'volumeID': 'TEST_PREFIX/TEST_VOLUME_ID'},
                'claimRef': {
                    'apiVersion': 'TEST_CLAIM_VERSION',
                    'kind': 'TEST_KIND',
                    'name': 'TEST_NAME',
                    'namespace': 'TEST_NAMESPACE'
                }
            }
        }

        volume.lock_volumes('prod', 'project-tools', ['test-jenkins', 'test-nginx-ingress'], None)

        mock_get_resources.assert_has_calls([
            call('pvc', 'project-tools-test-namespace', 'release', 'project-tools-test-namespace-test-jenkins'),
            call('pvc', 'project-tools-test-namespace', 'release', 'project-tools-test-namespace-test-nginx-ingress')
        ])
        mock_get_resource_by_name.assert_has_calls([
            call('pv', 'TEST_VOLUME_ID_NAME_1'),
            call('pv', 'TEST_VOLUME_ID_NAME_1')
        ])
        mock_delete_ec2_tags.assert_has_calls([
            call('TEST_VOLUME_ID',
                 ['kubernetes.io/cluster/cl1.tools.test.com', 'KubernetesCluster', 'LockedOnCluster']),
            call('TEST_VOLUME_ID',
                 ['kubernetes.io/cluster/cl1.tools.test.com', 'KubernetesCluster', 'LockedOnCluster'])
        ])
        mock_create_ec2_tags.assert_has_calls([
            call('TEST_VOLUME_ID', {'LockedOnCluster': 'cl1.tools.test.com'}),
            call('TEST_VOLUME_ID', {'LockedOnCluster': 'cl1.tools.test.com'})
        ])
        mock_save_content_to_s3.assert_has_calls([
            call('apiVersion: TEST_API_VERSION\n'
                 'kind: PersistentVolume\n'
                 'metadata:\n'
                 '  name: TEST_VOLUME_ID_NAME\n'
                 'spec:\n  awsElasticBlockStore:\n'
                 '    volumeID: TEST_PREFIX/TEST_VOLUME_ID\n'
                 '  claimRef:\n'
                 '    apiVersion: TEST_CLAIM_VERSION\n'
                 '    kind: TEST_KIND\n'
                 '    name: TEST_NAME\n'
                 '    namespace: TEST_NAMESPACE\n'
                 '  persistentVolumeReclaimPolicy: Retain',
                 'persistent-volumes.tools.test.com',
                 'prod_project-tools_test-jenkins.yaml'),
            call('apiVersion: TEST_API_VERSION\n'
                 'kind: PersistentVolume\n'
                 'metadata:\n'
                 '  name: TEST_VOLUME_ID_NAME\n'
                 'spec:\n'
                 '  awsElasticBlockStore:\n'
                 '    volumeID: TEST_PREFIX/TEST_VOLUME_ID\n'
                 '  claimRef:\n'
                 '    apiVersion: TEST_CLAIM_VERSION\n'
                 '    kind: TEST_KIND\n'
                 '    name: TEST_NAME\n'
                 '    namespace: TEST_NAMESPACE\n'
                 '  persistentVolumeReclaimPolicy: Retain',
                 'persistent-volumes.tools.test.com',
                 'prod_project-tools_test-nginx-ingress.yaml')
        ])
        mock_print_action.assert_has_calls([
            call("Locking persistent volumes: ['TEST_VOLUME_ID_NAME_1']"),
            call('Setting persistent volume reclaim policy for TEST_VOLUME_ID_NAME to Retain'),
            call('Releasing persistent volume TEST_VOLUME_ID_NAME from Kops.'),
            call('Saving persistent volume definition to '
                 's3://persistent-volumes.tools.test.com/prod_project-tools_test-jenkins.yaml'),
            call("Locking persistent volumes: ['TEST_VOLUME_ID_NAME_1']"),
            call('Setting persistent volume reclaim policy for TEST_VOLUME_ID_NAME to Retain'),
            call('Releasing persistent volume TEST_VOLUME_ID_NAME from Kops.'),
            call('Saving persistent volume definition to '
                 's3://persistent-volumes.tools.test.com/prod_project-tools_test-nginx-ingress.yaml')
        ])
        mock_print_details.assert_called()


class TestUnlockVolumes(TestCase):

    @patch('aloft.volume.k8s.get_resources')
    @patch('aloft.volume.k8s.get_resource_by_name')
    @patch('aloft.volume.aws.delete_ec2_tags')
    @patch('aloft.volume.aws.create_ec2_tags')
    @patch('aloft.volume.aws.delete_file_in_s3')
    @patch('aloft.volume.output.print_action')
    def test_should_lock_volumess(self,
                                  mock_print_action,
                                  mock_delete_file_in_s3,
                                  mock_create_ec2_tags,
                                  mock_delete_ec2_tags,
                                  mock_get_resource_by_name,
                                  mock_get_resources):

        os.environ['ALOFT_CONFIG'] = f'test-config'
        mock_get_resources.return_value = [{'spec': {'volumeName': 'TEST_VOLUME_ID_NAME_1'}}]
        mock_get_resource_by_name.return_value = {
            'apiVersion': 'TEST_API_VERSION',
            'kind': 'PersistentVolume',
            'metadata': {'name': 'TEST_VOLUME_ID_NAME'},
            'spec': {
                'persistentVolumeReclaimPolicy': 'Delete',
                'awsElasticBlockStore': {'volumeID': 'TEST_PREFIX/TEST_VOLUME_ID'},
                'claimRef': {
                    'apiVersion': 'TEST_CLAIM_VERSION',
                    'kind': 'TEST_KIND',
                    'name': 'TEST_NAME',
                    'namespace': 'TEST_NAMESPACE'
                }
            }
        }

        volume.unlock_volumes('prod', 'project-tools', ['test-jenkins', 'test-nginx-ingress'], None)

        mock_get_resources.assert_has_calls([
            call('pvc', 'project-tools-test-namespace', 'release', 'project-tools-test-namespace-test-jenkins'),
            call('pvc', 'project-tools-test-namespace', 'release', 'project-tools-test-namespace-test-nginx-ingress')
        ])
        mock_get_resource_by_name.assert_has_calls([
            call('pv', 'TEST_VOLUME_ID_NAME_1'),
            call('pv', 'TEST_VOLUME_ID_NAME_1')
        ])
        mock_delete_ec2_tags.assert_has_calls([
            call('TEST_VOLUME_ID',
                 ['kubernetes.io/cluster/cl1.tools.test.com', 'KubernetesCluster', 'LockedOnCluster']),
            call('TEST_VOLUME_ID',
                 ['kubernetes.io/cluster/cl1.tools.test.com', 'KubernetesCluster', 'LockedOnCluster'])
        ])
        mock_create_ec2_tags.assert_has_calls([
            call('TEST_VOLUME_ID',
                 {'kubernetes.io/cluster/cl1.tools.test.com': 'owned', 'KubernetesCluster': 'cl1.tools.test.com'}),
            call('TEST_VOLUME_ID',
                 {'kubernetes.io/cluster/cl1.tools.test.com': 'owned', 'KubernetesCluster': 'cl1.tools.test.com'})
        ])
        mock_delete_file_in_s3.assert_has_calls([
            call('persistent-volumes.tools.test.com', 'prod_project-tools_test-jenkins.yaml'),
            call('persistent-volumes.tools.test.com', 'prod_project-tools_test-nginx-ingress.yaml')
        ])
        mock_print_action.assert_has_calls([
            call("Unlocking persistent volumes: ['TEST_VOLUME_ID_NAME_1']"),
            call('Setting persistent volume reclaim policy for TEST_VOLUME_ID_NAME to Delete'),
            call('Attaching persistent volume TEST_VOLUME_ID_NAME to Kops.'),
            call('Deleting persistent volume definition from '
                 's3://persistent-volumes.tools.test.com/prod_project-tools_test-jenkins.yaml'),
            call("Unlocking persistent volumes: ['TEST_VOLUME_ID_NAME_1']"),
            call('Setting persistent volume reclaim policy for TEST_VOLUME_ID_NAME to Delete'),
            call('Attaching persistent volume TEST_VOLUME_ID_NAME to Kops.'),
            call('Deleting persistent volume definition from '
                 's3://persistent-volumes.tools.test.com/prod_project-tools_test-nginx-ingress.yaml')
        ])


class TestRestoreVolumes(TestCase):

    def test_should_restore_volume(self):
        pass


class TestRemoveReleasedVolumeResources(TestCase):

    def test_should_remove_released_volume_resources(self):
        pass
