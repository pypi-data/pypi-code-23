from Adafruit_BME280 import *
from Adafruit_CCS811 import Adafruit_CCS811
from bme280_exporter import BME280Exporter
from ccs811_exporter import CCS811Exporter
import logging

BME280_ADDRESS_OPEN = 0x77
BME280_ADDRESS_CLOSED = 0x76
CCS811_ADDRESS_OPEN = 0x5B
CCS811_ADDRESS_CLOSED = 0x5A

logger = logging.getLogger(__name__)


class SEN14348Exporter:
    """Collects and exports Prometheus metrics for a SparkFun Environmental Combo Breakout (SEN-14348)"""
    def __init__(self, labels=None,
                 bme280=BME280(address=BME280_ADDRESS_OPEN),
                 ccs811=Adafruit_CCS811(address=CCS811_ADDRESS_OPEN)):
        self.bme280 = BME280Exporter(bme280, labels=labels)
        self.ccs811 = CCS811Exporter(ccs811, labels=labels)

    def measure(self):
        """Read measurements from BME280 and CCS811"""
        self.bme280.measure()
        self.ccs811.calibrate(self.bme280.temp, self.bme280.humidity)
        self.ccs811.measure()

    def export(self):
        """Export BME280/CCS811 metrics to Prometheus"""
        self.bme280.export()
        self.ccs811.export()
