from Adafruit_CCS811 import Adafruit_CCS811
import argparse
from ccs811_exporter import CCS811Exporter
import json
import logging
import prometheus_client
from time import sleep

_DEFAULT_I2C_ADDRESS = 0x5B
_DEFAULT_PORT = 9501
_DEFAULT_SAMPLE_INTERVAL = 2
_DEFAULT_TEMP_OFFSET = -25.0

logger = logging.getLogger('ccs811_exporter')


def _init_arg_parser():
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action='store_true',
                   help="increase output verbosity")
    p.add_argument("-p", "--port",
                   type=int, default=_DEFAULT_PORT,
                   help="exporter port (default: {})"
                        .format(_DEFAULT_PORT))
    p.add_argument("-a", "--address",
                   type=lambda x: int(x, 0), default=_DEFAULT_I2C_ADDRESS,
                   help="CCS811 I2C address (default: 0x{:02x})"
                        .format(_DEFAULT_I2C_ADDRESS))
    p.add_argument("-l", "--labels", type=json.loads,
                   help="JSON object of Prometheus labels to apply")
    p.add_argument("-i", "--interval",
                   type=int, default=_DEFAULT_SAMPLE_INTERVAL,
                   help="measurement sample interval (default: {})"
                        .format(_DEFAULT_SAMPLE_INTERVAL))
    p.add_argument("-to", type=float, default=_DEFAULT_TEMP_OFFSET,
                   help="temperature offset (default: {:.1f}"
                        .format(_DEFAULT_TEMP_OFFSET))
    return p


def _configure_logger(args):
    f = logging.Formatter('%(asctime)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(f)
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    logger.addHandler(ch)


def main():
    parser = _init_arg_parser()
    args = parser.parse_args()

    _configure_logger(args)

    logger.info("initializing CCS811 at 0x{a:02x}".format(a=args.address))
    ccs811 = Adafruit_CCS811(address=args.address)

    logger.info("initializing CCS811 exporter with labels {}".format(args.labels))
    exporter = CCS811Exporter(ccs811, labels=args.labels)

    logger.info("waiting for CCS811")
    exporter.wait()

    logger.info("setting temperature offset to {:.1f}".format(args.to))
    temp = ccs811.calculateTemperature()
    ccs811.tempOffset = temp + args.to
    
    logger.info("starting exporter on port {}".format(args.port))
    prometheus_client.start_http_server(args.port)

    logger.info("starting sampling with {}s interval".format(args.interval))
    while True:
        exporter.measure()
        exporter.export()
        sleep(args.interval)


if __name__ == "__main__":
    main()
