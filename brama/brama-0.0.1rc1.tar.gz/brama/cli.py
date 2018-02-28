import argparse

from .app import Brama

parser = argparse.ArgumentParser(description='Brama API Gateway')
parser.add_argument('--config', '-c', dest='config', help='Path to config',
                    required=True)
parser.add_argument('--plugins', dest='plugins',
                    help='Path to plugins python modules')
parser.add_argument('--host', '-s', dest='host', help='Host',
                    default='0.0.0.0')
parser.add_argument('--port', '-p', dest='port', help='Port', default=8051,
                    type=int)
parser.add_argument('--workers', '-w', dest='workers', help='Workers num',
                    default=1, type=int)
parser.add_argument('--debug', dest='debug', help='Debug', action='store_true')

args = parser.parse_args()

brama = Brama('brama')
brama.load_config(args.config)
brama.load_plugins(args.plugins)


def main():
    brama.run(args.host, args.port, debug=args.debug, workers=args.workers)


if __name__ == '__main__':
    main()
