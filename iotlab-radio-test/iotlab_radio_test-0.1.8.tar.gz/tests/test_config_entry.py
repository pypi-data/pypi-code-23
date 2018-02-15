import json
import tempfile
import unittest
from argparse import ArgumentTypeError

from iotlab_radio_test.cli import parser
from iotlab_radio_test.config import get_config_from_yaml


class TestConfigEntry(unittest.TestCase):
    def test_user_specified_config_file(self):
        self.maxDiff = None
        config_file = tempfile.mktemp()
        open(config_file, 'w').write(
            '''site: saclay
nodes_str: 42
duration: 55
radio:
  packet_size: 12
draw:
  azim: 4
''')
        testargs = ['start', '--config', config_file]
        arguments = parser.parse_args(testargs)
        assert arguments.command == 'start'
        expected = get_config_from_yaml()
        expected.site = 'saclay'
        expected.duration = 55
        expected.node_list = [42]
        expected.radio.packet_size = 12
        expected.draw.azim = 4.0
        self.assertDictEqual(expected.to_dict(), arguments.config.to_dict())

    def test_user_specified_config_cli(self):
        self.maxDiff = None
        testargs = ['aggregate_avg', '-l', '10', '11', '-n', 'test_name',
                    '--site', 'lille', '--nodes_str', '12-14+17',
                    '--radio.txpower_list', '0','3']
        arguments = parser.parse_args(testargs)
        self.assertIsNotNone(arguments)
        assert arguments.command == 'aggregate_avg'
        expected = get_config_from_yaml()
        expected.site = 'lille'
        expected.node_list = [12, 13, 14, 17]
        expected.radio.txpower_list = [0, 3]
        self.assertDictEqual(expected.to_dict(), arguments.config.to_dict())

    def test_validate_site_config(self):
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start', '--site', 'invalidsite']))

        arguments = parser.parse_args(['start', '--site', 'lille'])
        self.assertIsNotNone(arguments)

    def test_validate_archi_config(self):
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start', '--archi', 'invalidarchi']))

        arguments = parser.parse_args(['start', '--archi', 'm3'])
        self.assertIsNotNone(arguments)

    def test_validate_node_list(self):
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start', '--nodes_str', '0.1;0.4']))
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start', '--nodes_str', '0.1,0.4']))
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start', '--nodes_str', 'invalid']))
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start', '--nodes_str', '8-2']))

        self.assertIsNotNone(parser.parse_args(['start', '--nodes_str', '1-3']))
        self.assertIsNotNone(parser.parse_args(['start', '--nodes_str', '1']))
        self.assertIsNotNone(parser.parse_args(['start', '--nodes_str', '10+17+24-26']))

    def test_validate_txpower_list_config(self):
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start', '--radio.txpower_list', '-18']))

        test_args = ['start',
                     '--radio.txpower_list',
                     '-17', '-12', '-9', '-7', '-5', '-4', '-3', '-2', '-1', '0', '0.7', '1.3', '1.8', '2.3', '3']
        self.assertIsNotNone(parser.parse_args(test_args))

    def test_validate_xyzname(self):
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start',
                                                                        '--draw.robots','invalid' ]))

        robot1 = json.dumps({'X': 1, 'Y': 1, 'Z': 1, 'Name': 'robot1'})
        robot2 = json.dumps({'X': 2, 'Y': 1, 'Z': 1, 'Name': 'robot2'})
        self.assertIsNotNone(parser.parse_args(['start','--draw.robots', robot1, robot2]))

    def test_validate_channel_list_config(self):
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start', '--radio.channel_list', '5']))
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start', '--radio.channel_list', '5;7']))
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start', '--radio.channel_list', '28']))
        self.assertRaises(SystemExit, lambda: parser.parse_args(['start', '--radio.channel_list', '28,48']))

        self.assertIsNotNone(parser.parse_args(['start', '--radio.channel_list', '15', '18', '21']))
