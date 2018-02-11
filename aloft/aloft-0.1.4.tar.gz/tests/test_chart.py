import os
from aloft import chart
from unittest import TestCase
from unittest.mock import call, patch


class TestApplyCharts(TestCase):

    @patch('aloft.chart.volume.restore_volumes')
    @patch('aloft.chart.k8s.create_namespace')
    @patch('aloft.chart.execute')
    @patch('aloft.chart.chart_config.generate_value_files')
    @patch('aloft.chart.aws.get_secret')
    @patch('aloft.chart.volume.lock_volumes')
    @patch('aloft.chart.output.print_action')
    def test_should_apply_charts(self,
                                 mock_print_action,
                                 mock_lock_volumes,
                                 mock_get_secret,
                                 mock_generate_value_files,
                                 mock_execute,
                                 mock_create_namespace,
                                 mock_restore_volumes):

        os.environ['ALOFT_CONFIG'] = f'test-config'
        mock_execute.return_value = ''
        mock_generate_value_files.return_value = ['TEST_VALUE_FILE_1', 'TEST_VALUE_FILE_2', 'TEST_VALUE_FILE_3']
        mock_get_secret.side_effect = [
            'TEST_GIT_USERNAME', 'TEST_GIT_PASSWORD', 'TEST_DOCKER_USERNAME', 'TEST_DOCKER_PASSWORD'
        ]

        chart.apply_charts('prod', 'project-tools', ['test-jenkins', 'test-nginx-ingress'], None)

        mock_execute.assert_has_calls([
            call('kubectl -n project-tools-test-namespace delete secret test-jenkins-secrets',
                 ['NotFound'], quiet=True),
            call('kubectl -n project-tools-test-namespace create secret generic test-jenkins-secrets'
                 '  --from-literal=git-username=TEST_GIT_USERNAME'
                 ' --from-literal=git-password=TEST_GIT_PASSWORD'
                 ' --from-literal=docker-username=TEST_DOCKER_USERNAME'
                 ' --from-literal=docker-password=TEST_DOCKER_PASSWORD', quiet=True),
            call('helm dependencies build test-config/charts/test-jenkins'),
            call('helm upgrade -i project-tools-test-namespace-test-jenkins'
                 ' --namespace project-tools-test-namespace test-config/charts/test-jenkins'
                 ' -f TEST_VALUE_FILE_1 -f TEST_VALUE_FILE_2 -f TEST_VALUE_FILE_3'),
            call('helm dependencies build test-config/charts/test-nginx-ingress'),
            call('helm upgrade -i project-tools-test-namespace-test-nginx-ingress'
                 ' --namespace project-tools-test-namespace test-config/charts/test-nginx-ingress'
                 ' -f TEST_VALUE_FILE_1 -f TEST_VALUE_FILE_2 -f TEST_VALUE_FILE_3')
        ])
        mock_create_namespace.assert_called_once_with('project-tools-test-namespace')
        mock_get_secret.assert_has_calls([
            call('project-tools.git-username'),
            call('project-tools.git-password'),
            call('project-tools.docker-username'),
            call('project-tools.docker-password')
        ])
        mock_restore_volumes.assert_called_once_with('prod',
                                                     'project-tools',
                                                     ['test-jenkins',
                                                      'test-nginx-ingress'],
                                                     None)
        mock_lock_volumes.assert_called_once_with('prod', 'project-tools', ['test-jenkins', 'test-nginx-ingress'], None)
        mock_print_action.assert_has_calls([
            call('Creating secret test-jenkins-secrets with keys'
                 ' [\'git-username\', \'git-password\', \'docker-username\', \'docker-password\']')
        ])


class TestDeleteCharts(TestCase):

    @patch('aloft.chart.execute')
    @patch('aloft.chart.k8s.delete_namespace_if_empty')
    @patch('aloft.chart.volume.remove_released_volume_resources')
    def test_should_delete_charts(self, mock_remove, mock_delete_namespace_if_empty, mock_execute):
        os.environ['ALOFT_CONFIG'] = f'test-config'

        chart.delete_charts('prod', 'project-tools', ['test-jenkins', 'test-nginx-ingress'], None)

        mock_execute.assert_has_calls([
            call('helm delete --purge project-tools-test-namespace-test-jenkins', ['not found']),
            call('kubectl -n project-tools-test-namespace delete secret test-jenkins-secrets', ['NotFound']),
            call('helm delete --purge project-tools-test-namespace-test-nginx-ingress', ['not found'])
        ])
        mock_delete_namespace_if_empty.assert_called_once_with('project-tools-test-namespace')
        mock_remove.assert_called_once_with('prod', 'project-tools', ['test-jenkins', 'test-nginx-ingress'], None)
