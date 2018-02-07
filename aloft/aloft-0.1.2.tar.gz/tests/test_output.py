from aloft import output
from unittest import TestCase
from unittest.mock import call, patch


class TestPrintOutput(TestCase):

    @patch('aloft.output.print')
    def test_should_print_action(self, mock_print):
        output.print_action('TEST_ACTION')

        mock_print.assert_called_once_with('**** TEST_ACTION\n')

    @patch('aloft.output.print')
    def test_should_print_details(self, mock_print):
        output.print_details('TEST_DETAIL_LINE_1\nTEST_DETAIL_LINE_2\nTEST_DETAIL_LINE_3')

        mock_print.assert_has_calls([
            call('     TEST_DETAIL_LINE_1'),
            call('     TEST_DETAIL_LINE_2'),
            call('     TEST_DETAIL_LINE_3')
        ])

    @patch('aloft.output.print')
    def test_should_print_detail_line(self, mock_print):
        output.print_details_line('TEST_DETAIL_LINE_1')

        mock_print.assert_called_once_with('     TEST_DETAIL_LINE_1')


class TestPrintTable(TestCase):

    @patch('aloft.output.print')
    def test_should_print_table(self, mock_print):
        output.print_table(
            ['HEADING_A', 'HEADING_B', 'HEADING_C'],
            [
                ['VALUE_1_1', 'VALUE_1_2', 'VALUE_1_3'],
                ['VALUE_2_1', 'VALUE_2_2', 'VALUE_2_3'],
                ['VALUE_3_1', 'VALUE_3_2', 'VALUE_3_3'],
                ['VALUE_4_1', 'VALUE_4_2', 'VALUE_4_3']
            ], '{0: <40} {1: <10} {2: <18}')

        mock_print.assert_has_calls([
            call('HEADING_A                                HEADING_B  HEADING_C         '),
            call('VALUE_1_1                                VALUE_1_2  VALUE_1_3         '),
            call('VALUE_2_1                                VALUE_2_2  VALUE_2_3         '),
            call('VALUE_3_1                                VALUE_3_2  VALUE_3_3         '),
            call('VALUE_4_1                                VALUE_4_2  VALUE_4_3         '),
        ])


class TestPrintYamlList(TestCase):

    @patch('aloft.output.print')
    def test_should_print_list_as_yaml(self, mock_print):
        output.print_list_as_yaml([
            {'TEST_KEY_1': 'TEST_VALUE_1'},
            {'TEST_KEY_2': 'TEST_VALUE_2'},
            {'TEST_KEY_3': 'TEST_VALUE_3'}
        ])

        mock_print.assert_called_once_with('TEST_KEY_1: TEST_VALUE_1\n'
                                           '---\n'
                                           'TEST_KEY_2: TEST_VALUE_2\n'
                                           '---\n'
                                           'TEST_KEY_3: TEST_VALUE_3')
