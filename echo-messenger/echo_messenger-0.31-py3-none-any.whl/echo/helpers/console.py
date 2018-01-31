import argparse
from random import randint

DEFAULT_IP = '0.0.0.0'
DEFAULT_PORT = 6665


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a',
        '--address',
        default=DEFAULT_IP,
        nargs='?',
        help='IP (default {})'.format(DEFAULT_IP))
    parser.add_argument(
        '-p',
        '--port',
        default=DEFAULT_PORT,
        nargs='?',
        help='Port (default {})'.format(DEFAULT_PORT))
    parser.add_argument(
        '-u',
        '--user',
        default='Anonymous_{}'.format(randint(1, 1000)),
        nargs='?',
        help='User name (default Anonymous_XXXX)')
    parser.add_argument(
        '-m',
        '--mode',
        default='console',
        nargs='?',
        choices=['server', 'gui_client', 'console_client'],
        help='Mode: Server, GUI client, Console client (default Console client)')
    return parser.parse_args()
