from aloft import input
from unittest import TestCase
from unittest.mock import Mock, patch


class TestGetDirectoryFromEnvironment(TestCase):

    @patch('aloft.input.os')
    def test_should_return_directory_path_if_exists(self, mock_os):
        mock_os.environ = {'TEST_KEY': 'TEST_PATH'}
        mock_os.path.expanduser = Mock(return_value='TEST_EXPANDED_PATH')
        mock_os.path.isdir = Mock(return_value=True)

        directory = input.get_directory_from_environment('TEST_KEY')

        self.assertEqual('TEST_EXPANDED_PATH', directory)
        mock_os.path.expanduser.assert_called_once_with('TEST_PATH')

    @patch('aloft.input.os')
    def test_should_raise_if_not_a_directory(self, mock_os):
        mock_os.environ = {'TEST_KEY': 'TEST_PATH'}
        mock_os.path.expanduser = Mock(return_value='TEST_EXPANDED_PATH')
        mock_os.path.isdir = Mock(return_value=False)

        with self.assertRaises(NotADirectoryError) as cm:
            input.get_directory_from_environment('TEST_KEY')

        self.assertEqual('TEST_KEY must reference a directory: TEST_EXPANDED_PATH', str(cm.exception))

    @patch('aloft.input.os')
    def test_should_raise_if_environment_variable_not_found(self, mock_os):
        mock_os.environ = {'TEST_KEY': None}
        mock_os.path.expanduser = Mock(return_value=None)
        mock_os.path.isdir = Mock(return_value=False)

        with self.assertRaises(NotADirectoryError) as cm:
            input.get_directory_from_environment('TEST_KEY')

        self.assertEqual('TEST_KEY environment variable has not been set', str(cm.exception))


class TestRenderTemplateFile(TestCase):

    @patch('aloft.input.jinja2', return_value=Mock())
    def test_should_render_template(self, mock_jinja2):
        mock_jinja2.render = Mock(return_value='TEST_RENDERED_CONTENT')
        mock_jinja2.get_template = Mock(return_value=mock_jinja2)
        mock_jinja2.Environment = Mock(return_value=mock_jinja2)
        mock_jinja2.FileSystemLoader = Mock(return_value='TEST_LOADER')

        context = {
            'TEST_KEY_1': 'TEST_VALUE_1',
            'TEST_KEY_2': 'TEST_VALUE_2',
            'TEST_KEY_3': 'TEST_VALUE_3'
        }
        output = input.render_template_file('TEST_TEMPLATE_PATH/TEST_TEMPLATE_FILENAME', context)

        self.assertEqual('TEST_RENDERED_CONTENT', output)
        mock_jinja2.FileSystemLoader.assert_called_once_with('TEST_TEMPLATE_PATH')
        mock_jinja2.Environment.assert_called_once_with(loader='TEST_LOADER')
        mock_jinja2.get_template.assert_called_once_with('TEST_TEMPLATE_FILENAME')
        mock_jinja2.render.assert_called_once_with(context)
