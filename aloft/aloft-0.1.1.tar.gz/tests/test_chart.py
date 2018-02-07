import os
from aloft import chart
from unittest import TestCase
from unittest.mock import call, patch


class TestApplyCharts(TestCase):

    @patch('aloft.chart.volume.restore_volumes')
    @patch('aloft.chart.k8s.create_namespace')
    @patch('aloft.chart.execute')
    @patch('aloft.chart.chart_config.generate_value_files')
    def test_should_apply_charts(self,
                                 mock_generate_value_files,
                                 mock_execute,
                                 mock_create_namespace,
                                 mock_restore_volumes):

        os.environ['ALOFT_CONFIG'] = f'test-config'
        mock_execute.return_value = ''
        mock_generate_value_files.return_value = ['TEST_VALUE_FILE_1', 'TEST_VALUE_FILE_2', 'TEST_VALUE_FILE_3']

        chart.apply_charts('prod', 'project-tools', ['test-jenkins', 'test-nginx-ingress'], None, False)

        mock_execute.assert_has_calls([
            call('helm dependencies build test-config/charts/test-jenkins'),
            call('helm upgrade --wait -i project-tools-test-namespace-test-jenkins '
                 '--namespace project-tools-test-namespace test-config/charts/test-jenkins '
                 '-f TEST_VALUE_FILE_1 -f TEST_VALUE_FILE_2 -f TEST_VALUE_FILE_3'),
            call('helm dependencies build test-config/charts/test-nginx-ingress'),
            call('helm upgrade --wait -i project-tools-test-namespace-test-nginx-ingress '
                 '--namespace project-tools-test-namespace test-config/charts/test-nginx-ingress '
                 '-f TEST_VALUE_FILE_1 -f TEST_VALUE_FILE_2 -f TEST_VALUE_FILE_3')
        ])
        mock_create_namespace.assert_called_once_with('project-tools-test-namespace')
        mock_restore_volumes.assert_called_once_with('prod',
                                                     'project-tools',
                                                     ['test-jenkins',
                                                      'test-nginx-ingress'],
                                                     None)


class TestDeleteCharts(TestCase):

    @patch('aloft.chart.execute')
    @patch('aloft.chart.k8s.delete_namespace_if_empty')
    @patch('aloft.chart.volume.remove_released_volume_resources')
    def test_should_delete_charts(self, mock_remove, mock_delete_namespace_if_empty, mock_execute):
        os.environ['ALOFT_CONFIG'] = f'test-config'

        chart.delete_charts('prod', 'project-tools', ['test-jenkins', 'test-nginx-ingress'], None)

        mock_execute.assert_has_calls([
            call('helm delete --purge project-tools-test-namespace-test-jenkins', ['not found']),
            call('helm delete --purge project-tools-test-namespace-test-nginx-ingress', ['not found'])
        ])
        mock_delete_namespace_if_empty.assert_called_once_with('project-tools-test-namespace')
        mock_remove.assert_called_once_with('prod', 'project-tools', ['test-jenkins', 'test-nginx-ingress'], None)
