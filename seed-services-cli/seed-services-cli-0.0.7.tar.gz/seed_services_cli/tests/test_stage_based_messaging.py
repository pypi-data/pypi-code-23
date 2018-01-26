""" Tests for seed_services_cli.stage_based_messaging """

import tempfile

from unittest import TestCase
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from click.testing import CliRunner
from seed_services_cli.main import cli


class TestStageBasedMessagingCommands(TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass


class TestSbmSchedules(TestStageBasedMessagingCommands):

    def test_schedule_list_help(self):
        result = self.runner.invoke(cli, ['sbm-schedules', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "List all schedules"
            in result.output)

    @patch('seed_services_client.StageBasedMessagingApiClient.get_schedules')
    def test_schedule_list(self, schedule_patch):
        schedule_patch.return_value = {'results': [{
            'id': '1',
            'minute': '2',
            'hour': '3',
            'day_of_week': '4',
            'day_of_month': '5',
            'month_of_year': '6',
        }]}

        result = self.runner.invoke(cli, ['sbm-schedules'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Found 1 results' in result.output)
        self.assertTrue('1: 2 3 4 5 6 (m/h/d/dM/MY)' in result.output)


class TestSbmMessagesets(TestStageBasedMessagingCommands):

    def test_messageset_list_help(self):
        result = self.runner.invoke(cli, ['sbm-messagesets', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "List all messagesets"
            in result.output)

    @patch('seed_services_client.StageBasedMessagingApiClient.get_messagesets')
    def test_messageset_list(self, messageset_patch):
        messageset_patch.return_value = {'results': [{
            'id': '1',
            'short_name': 'test_set',
            'content_type': 'text',
            'next_set': '4',
            'default_schedule': '5',
            'notes': 'good set',
        }]}

        result = self.runner.invoke(cli, ['sbm-messagesets'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Found 1 results' in result.output)
        self.assertTrue('1,test_set,text,4,5,good set' in result.output)


class TestSbmMessages(TestStageBasedMessagingCommands):

    def test_message_list_help(self):
        result = self.runner.invoke(cli, ['sbm-messages', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "List all messages"
            in result.output)

    @patch('seed_services_client.StageBasedMessagingApiClient.get_message')
    def test_message_list_specific_message(self, message_patch):
        message_patch.return_value = {
            'id': '1',
            'messageset': '2',
            'sequence_number': '3',
            'lang': 'eng_ZA',
            'text_content': 'test message',
            'binary_content': 'binary',
        }

        result = self.runner.invoke(cli, ['sbm-messages', '--message=1'])
        self.assertEqual(result.exit_code, 0)
        message_patch.assert_called_with(message_id=1)
        self.assertTrue('Found 1 results' in result.output)
        self.assertTrue('1,2,3,eng_ZA,"test message",binary' in result.output)

    @patch('seed_services_client.StageBasedMessagingApiClient.get_messages')
    def test_message_list_all_messages(self, messages_patch):
        messages_patch.return_value = {'results': [
            {
                'id': '1',
                'messageset': '2',
                'sequence_number': '3',
                'lang': 'eng_ZA',
                'text_content': 'test message',
                'binary_content': 'binary',
            }, {
                'id': '2',
                'messageset': '2',
                'sequence_number': '3',
                'lang': 'eng_ZA',
                'text_content': 'test msg two',
                'binary_content': 'binary',
            }
        ]}

        result = self.runner.invoke(cli, ['sbm-messages'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Found 2 results' in result.output)
        self.assertTrue('1,2,3,eng_ZA,"test message",binary' in result.output)
        self.assertTrue('2,2,3,eng_ZA,"test msg two",binary' in result.output)


class TestSbmMessagesDelete(TestStageBasedMessagingCommands):

    def test_message_delete_help(self):
        result = self.runner.invoke(cli, ['sbm-messages-delete', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Delete all messages matching filter"
            in result.output)

    @patch('seed_services_client.StageBasedMessagingApiClient.delete_message')
    @patch('seed_services_client.StageBasedMessagingApiClient.get_message')
    def test_message_delete(self, get_patch, delete_patch):
        get_patch.return_value = {'id': 1, 'binary_content': False}

        result = self.runner.invoke(
            cli, ['sbm-messages-delete', '--yes', '--message=1'])
        self.assertEqual(result.exit_code, 0)
        delete_patch.assert_called_with(message_id=1)
        self.assertTrue('Found 1 result(s)' in result.output)


class TestSbmMessagesImport(TestStageBasedMessagingCommands):

    def test_messages_import_help(self):
        result = self.runner.invoke(cli, ['sbm-messages-import', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Import to the Stage Based Messaging service."
            in result.output)

    def test_message_import_error_with_no_param(self):
        result = self.runner.invoke(cli, ['sbm-messages-import'])
        self.assertEqual(result.exit_code, 2)
        self.assertTrue(
            'Please specify either --csv or --json.' in result.output)

    @patch('seed_services_client.StageBasedMessagingApiClient.create_message')
    def test_message_import_csv(self, create_patch):
        csv_file = tempfile.NamedTemporaryFile()
        csv_file.write(
            b'messageset,sequence_number,lang,text_content,binary_content\n')
        csv_file.write(b'1,2,eng_ZA,"message text",""')
        csv_file.flush()

        result = self.runner.invoke(
            cli, ['sbm-messages-import', '--csv={0}'.format(csv_file.name)])
        csv_file.close()

        self.assertEqual(result.exit_code, 0)
        create_patch.assert_called_with({
            'lang': 'eng_ZA',
            'text_content': 'message text',
            'messageset': '1',
            'sequence_number': '2',
            'binary_content': '',
        })


class TestSbmMessagesUpdate(TestStageBasedMessagingCommands):

    def test_messages_update_help(self):
        result = self.runner.invoke(cli, ['sbm-messages-update', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Update messages in the Stage Based Messaging service."
            in result.output)

    def test_message_update_error_with_no_param(self):
        result = self.runner.invoke(cli, ['sbm-messages-update'])
        self.assertEqual(result.exit_code, 2)
        self.assertTrue(
            'Please specify either --csv or --json.' in result.output)

    @patch('seed_services_client.StageBasedMessagingApiClient.update_message')
    @patch('seed_services_client.StageBasedMessagingApiClient.get_messages')
    def test_message_update_csv(self, get_patch, update_patch):

        get_patch.return_value = {'results': [
            {
                'id': 132,
                'binary_content': False,
                'lang': 'eng_ZA',
                'text_content': 'message text',
                'messageset': '1',
                'sequence_number': '2'
            }
        ]}

        csv_file = tempfile.NamedTemporaryFile()
        csv_file.write(
            b'messageset,sequence_number,lang,text_content,binary_content\n')
        csv_file.write(b'1,2,eng_ZA,"message text",""')
        csv_file.flush()

        result = self.runner.invoke(
            cli, ['sbm-messages-update', '--csv={0}'.format(csv_file.name)])
        csv_file.close()

        self.assertEqual(result.exit_code, 0)
        update_patch.assert_called_with(132, {
            'lang': 'eng_ZA',
            'text_content': 'message text',
            'messageset': '1',
            'sequence_number': '2',
            'binary_content': ''
        })

    @patch('seed_services_client.StageBasedMessagingApiClient.update_message')
    @patch('seed_services_client.StageBasedMessagingApiClient.get_messages')
    def test_message_update_csv_no_messages(self, get_patch, update_patch):
        """ Test that result output contains 'Error: Message not found.' error
            when no message is returned in a lookup.
        """
        get_patch.return_value = {'results': []}

        csv_file = tempfile.NamedTemporaryFile()
        csv_file.write(
            b'messageset,sequence_number,lang,text_content,binary_content\n')
        csv_file.write(b'1,2,eng_ZA,"message text",""')
        csv_file.flush()

        result = self.runner.invoke(
            cli, ['sbm-messages-update', '--csv={0}'.format(csv_file.name)])
        csv_file.close()

        self.assertEqual(result.exit_code, 2)
        self.assertTrue('Error: Message not found.' in result.output)

    @patch('seed_services_client.StageBasedMessagingApiClient.update_message')
    @patch('seed_services_client.StageBasedMessagingApiClient.get_messages')
    def test_message_update_csv_multiple_messages(self, get_patch,
                                                  update_patch):
        """ Test that result output contains 'Multiple messages found.' error
            when more than one message is returned in a lookup.
        """
        get_patch.return_value = {'results': [
            {
                'id': 137,
                'binary_content': False,
                'lang': 'eng_ZA',
                'text_content': 'message text 137',
                'messageset': '1',
                'sequence_number': '2'
            },
            {
                'id': 139,
                'binary_content': False,
                'lang': 'eng_ZA',
                'text_content': 'message text 139',
                'messageset': '1',
                'sequence_number': '2'
            }
        ]}

        csv_file = tempfile.NamedTemporaryFile()
        csv_file.write(
            b'messageset,sequence_number,lang,text_content,binary_content\n')
        csv_file.write(b'1,2,eng_ZA,"message text",""')
        csv_file.flush()

        result = self.runner.invoke(
            cli, ['sbm-messages-update', '--csv={0}'.format(csv_file.name)])
        csv_file.close()

        self.assertEqual(result.exit_code, 2)
        self.assertTrue('Error: Multiple messages found.' in result.output)

    @patch('seed_services_client.StageBasedMessagingApiClient.update_message')
    @patch('seed_services_client.StageBasedMessagingApiClient.get_messages')
    def test_message_update_json(self, get_patch, update_patch):
        """ Test that messages update command takes JSON as input.
        """
        get_patch.return_value = {'results': [
            {
                'id': 132,
                'binary_content': False,
                'lang': 'eng_ZA',
                'text_content': 'message text',
                'messageset': '1',
                'sequence_number': '2'
            }
        ]}

        json_file = tempfile.NamedTemporaryFile()
        json_file.write(
            b'{"binary_content": "", "lang": "eng_ZA", '
            b'"text_content": "message text", "messageset": "1", '
            b'"sequence_number": "2"}')
        json_file.flush()

        result = self.runner.invoke(
            cli, ['sbm-messages-update', '--json={0}'.format(json_file.name)])
        json_file.close()

        self.assertEqual(result.exit_code, 0)
        update_patch.assert_called_with(132, {
            'lang': 'eng_ZA',
            'text_content': 'message text',
            'messageset': '1',
            'sequence_number': '2',
            'binary_content': ''
        })
