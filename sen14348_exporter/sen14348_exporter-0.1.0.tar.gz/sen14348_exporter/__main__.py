from Adafruit_BME280 import *
from Adafruit_CCS811 import Adafruit_CCS811
import argparse
import sen14348_exporter
from sen14348_exporter import SEN14348Exporter
import json
import logging
import prometheus_client
from time import sleep

_DEFAULT_BME280_ADDRESS = sen14348_exporter.BME280_ADDRESS_OPEN
_DEFAULT_BME280_FILTER = 0
_DEFAULT_BME280_OVERSAMPLING = 4
_DEFAULT_CCS811_ADDRESS = sen14348_exporter.CCS811_ADDRESS_OPEN
_DEFAULT_CCS811_TEMP_OFFSET = -25.0
_DEFAULT_LOG_FORMAT = "%(asctime)s %(name)s - %(message)s"
_DEFAULT_PORT = 9502
_DEFAULT_SAMPLE_INTERVAL = 2

logger = logging.getLogger("sen14348_exporter")


def _init_arg_parser():
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action='store_true',
                   help="increase output verbosity")
    p.add_argument("-p", "--port",
                   type=int, default=_DEFAULT_PORT,
                   help="exporter port (default: {})".format(_DEFAULT_PORT))
    p.add_argument("-ba", "--bme-address",
                   type=lambda x: int(x, 0), default=_DEFAULT_BME280_ADDRESS,
                   help="BME280 I2C address (default: 0x{:02x})"
                        .format(_DEFAULT_BME280_ADDRESS))
    p.add_argument("-ca", "--ccs-address",
                   type=lambda x: int(x, 0), default=_DEFAULT_CCS811_ADDRESS,
                   help="CCS811 I2C address (default: 0x{:02x})"
                        .format(_DEFAULT_CCS811_ADDRESS))
    p.add_argument("-l", "--labels", type=json.loads,
                   help="JSON object of Prometheus labels to apply")
    p.add_argument("-i", "--interval",
                   type=int, default=_DEFAULT_SAMPLE_INTERVAL,
                   help="measurement sample interval (default: {})"
                        .format(_DEFAULT_SAMPLE_INTERVAL))
    p.add_argument("-bf", "--filter", type=int, default=_DEFAULT_BME280_FILTER,
                   help="BME280 filter value to apply (0-4, default: {})"
                        .format(_DEFAULT_BME280_FILTER))
    p.add_argument("-bho", type=int, default=_DEFAULT_BME280_OVERSAMPLING,
                   help="BME280 humidity oversampling value (1-5, default: {})"
                        .format(_DEFAULT_BME280_OVERSAMPLING))
    p.add_argument("-bpo", type=int, default=_DEFAULT_BME280_OVERSAMPLING,
                   help="BME280 pressure oversampling value (1-5, default: {})"
                        .format(_DEFAULT_BME280_OVERSAMPLING))
    p.add_argument("-bto", type=int, default=_DEFAULT_BME280_OVERSAMPLING,
                   help="BME280 temperature oversampling value (1-5, default: {})"
                        .format(_DEFAULT_BME280_OVERSAMPLING))
    p.add_argument("-cto", type=float, default=_DEFAULT_CCS811_TEMP_OFFSET,
                   help="CCS811 temperature offset (default: {:.1f})"
                        .format(_DEFAULT_CCS811_TEMP_OFFSET))
    return p


def _configure_logger(args):
    f = logging.Formatter(_DEFAULT_LOG_FORMAT)
    ch = logging.StreamHandler()
    ch.setFormatter(f)

    for log in [logger,
                logging.getLogger("bme280_exporter"),
                logging.getLogger("ccs811_exporter")]:
        log.setLevel(logging.DEBUG if args.verbose else logging.INFO)
        log.addHandler(ch)


def main():
    parser = _init_arg_parser()
    args = parser.parse_args()

    _configure_logger(args)
    logger.info("initializing BME280 at 0x{a:02x} filter: {f} oversampling(h: {h}, p: {p}, t: {t})"
                .format(a=args.bme_address,
                        f=args.filter,
                        h=args.bho,
                        p=args.bpo,
                        t=args.bto))

    bme280 = BME280(address=args.bme_address,
                    filter=args.filter,
                    h_mode=args.bho,
                    p_mode=args.bpo,
                    t_mode=args.bto)

    logger.info("initializing CCS811 at 0x{a:02x}".format(a=args.ccs_address))
    ccs811 = Adafruit_CCS811(address=args.ccs_address)

    logger.info("initializing SEN14348Exporter with labels {}".format(args.labels))
    exporter = SEN14348Exporter(labels=args.labels, bme280=bme280, ccs811=ccs811)

    if not exporter.ccs811.wait():
        logger.error("CCS811 is unavailable, exiting")
        return

    logger.info("setting temperature offset to {:.1f}".format(args.cto))
    temp = ccs811.calculateTemperature()
    ccs811.tempOffset = temp + args.cto

    logger.info('starting exporter on port {}'.format(args.port))
    prometheus_client.start_http_server(args.port)

    while True:
        exporter.measure()
        exporter.export()
        sleep(args.interval)


if __name__ == '__main__':
    main()
