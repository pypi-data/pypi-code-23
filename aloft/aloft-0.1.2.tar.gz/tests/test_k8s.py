from aloft import k8s
from unittest import TestCase
from unittest.mock import call, patch


class TestApplyFile(TestCase):

    @patch('aloft.k8s.execute')
    def test_should_apply_file(self, mock_execute):
        k8s.apply_file('TEST_FILENAME')

        mock_execute.assert_called_once_with('kubectl apply -f TEST_FILENAME')


class TestCreateNamespace(TestCase):

    @patch('aloft.k8s.execute')
    def test_should_create_namespace(self, mock_execute):
        k8s.create_namespace('TEST_NAMESPACE')

        mock_execute.assert_called_once_with('kubectl create namespace TEST_NAMESPACE', ['AlreadyExists'])


class TestDeleteNamespace(TestCase):

    @patch('aloft.k8s.execute')
    def test_should_always_delete_namespace(self, mock_execute):
        k8s.delete_namespace('TEST_NAMESPACE')

        mock_execute.assert_called_once_with('kubectl delete namespace TEST_NAMESPACE', ['NotFound'])

    @patch('aloft.k8s.execute')
    def test_should_delete_namespace_if_empty(self, mock_execute):
        mock_execute.return_value = ''

        k8s.delete_namespace_if_empty('TEST_NAMESPACE')

        mock_execute.assert_has_calls([
            call('helm ls -q --namespace TEST_NAMESPACE'),
            call('kubectl delete namespace TEST_NAMESPACE', ['NotFound'])
        ])

    @patch('aloft.k8s.execute')
    def test_should_not_delete_namespace_if_not_empty(self, mock_execute):
        mock_execute.return_value = 'TEST_EXISTING_CHART_NAME'

        k8s.delete_namespace_if_empty('TEST_NAMESPACE')

        mock_execute.assert_called_once_with('helm ls -q --namespace TEST_NAMESPACE')


class TestGetResources(TestCase):

    @patch('aloft.k8s.execute')
    def test_should_get_resource_by_label_if_exists(self, mock_execute):
        mock_execute.return_value = ('items:\n'
                                     ' - ITEM_1:\n'
                                     '    KEY_1: VALUE1\n'
                                     ' - ITEM_2:\n'
                                     '    KEY_1: VALUE1\n')
        selectors = [{'key': 'TEST_KEY', 'value': 'TEST_VALUE', 'operator': '='}]

        resources = k8s.get_resources('TEST_RESOURCE_TYPE', 'TEST_NAME_SPACE', selectors)

        mock_execute.assert_called_once_with('kubectl get TEST_RESOURCE_TYPE -n TEST_NAME_SPACE '
                                             '-l TEST_KEY=TEST_VALUE -o yaml', ['NotFound'])
        self.assertEqual([{'ITEM_1': {'KEY_1': 'VALUE1'}}, {'ITEM_2': {'KEY_1': 'VALUE1'}}], resources)

    @patch('aloft.k8s.execute')
    def test_should_return_empty_list_if_none_found(self, mock_execute):
        mock_execute.return_value = 'items: []'

        resources = k8s.get_resources('TEST_RESOURCE_TYPE', 'TEST_NAME_SPACE', None)

        mock_execute.assert_called_once_with('kubectl get TEST_RESOURCE_TYPE -n TEST_NAME_SPACE -o yaml', ['NotFound'])
        self.assertEqual([], resources)

    @patch('aloft.k8s.execute')
    def test_should_return_resource_by_name(self, mock_execute):
        mock_execute.return_value = ('ITEM_1:\n'
                                     '  KEY_1: VALUE1\n')

        resources = k8s.get_resource_by_name('TEST_RESOURCE_TYPE', 'TEST_NAME', 'TEST_NAME_SPACE')

        mock_execute.assert_called_once_with('kubectl get TEST_RESOURCE_TYPE TEST_NAME -n TEST_NAME_SPACE -o yaml',
                                             ['NotFound'])
        self.assertEqual({'ITEM_1': {'KEY_1': 'VALUE1'}}, resources)

    @patch('aloft.k8s.execute')
    def test_should_return_none_if_not_found_by_name(self, mock_execute):
        mock_execute.return_value = 'items: []'

        resources = k8s.get_resource_by_name('TEST_RESOURCE_TYPE', 'TEST_NAME', 'TEST_NAME_SPACE')

        mock_execute.assert_called_once_with('kubectl get TEST_RESOURCE_TYPE TEST_NAME -n TEST_NAME_SPACE -o yaml',
                                             ['NotFound'])
        self.assertEqual(None, resources)

    @patch('aloft.k8s.execute')
    def test_should_return_resource_by_name_without_namespace(self, mock_execute):
        mock_execute.return_value = ('ITEM_1:\n'
                                     '  KEY_1: VALUE1\n')

        resources = k8s.get_resource_by_name('TEST_RESOURCE_TYPE', resource_name='TEST_NAME')

        mock_execute.assert_called_once_with('kubectl get TEST_RESOURCE_TYPE TEST_NAME -o yaml', ['NotFound'])
        self.assertEqual({'ITEM_1': {'KEY_1': 'VALUE1'}}, resources)


class TestUseNamespace(TestCase):

    @patch('aloft.k8s.execute')
    def test_should_use_namespace(self, mock_execute):
        k8s.use_namespace('TEST_NAMESPACE')

        mock_execute.assert_called_once_with('kubectl config set-context'
                                             ' $(kubectl config current-context)'
                                             ' --namespace=TEST_NAMESPACE')

