import bme280 as bme280_driver  # https://pypi.python.org/pypi/RPi.bme280
from smbus2 import SMBus  # https://pypi.python.org/pypi/smbus2/0.2.0
from copreus.baseclasses.adriver import ADriver
from copreus.baseclasses.apolling import APolling
from copreus.baseclasses.calibratedvalue import CalibratedValue


class BME_280(ADriver, APolling):  # BME280 would result in a name conflict with the above imported driver ...
    """Driver for the BME280 sensor (temperature, humidity, and pressure) with i2c connectivity.

    The driver entry in the yaml file consists of:
      * ADriver entries
        * topics_pub: temperature, humidity, pressure
      * APolling entries
      * i2c entries:
        * port: i2c port
        * address: i2c address
      * CalibratedValue entries in a sub-block named 'calibration_temperature'
      * CalibratedValue entries in a sub-block named 'calibration_humidity'
      * CalibratedValue entries in a sub-block named 'calibration_pressure'
      * bme_280 own entries
        * use-calibration_temperature: if set to False, calibration will be ommitted.
        * use-calibration_humidity: if set to False, calibration will be ommitted.
        * use-calibration_pressure: if set to False, calibration will be ommitted.

    Example:
    device:
        poll-interval: 30
        type: bme_280
        port: 1
        address: 0x76
        topics-pub:
            temperature: /bme280/temperature/raw
            humidity: /bme280/humidity/raw
            pressure: /bme280/pressure/raw
        use-calibration-temperature: True
        calibration-temperature:
        # - [ref_value, raw_value]
        use-calibration-humidity: True
        calibration-humidity:
        # - [ref_value, raw_value]
        use-calibration-pressure: True
        calibration-pressure:
        # - [ref_value, raw_value]


    Note: this class is named BME_280 due to a name conflict with the used Adafruit driver named bme280.
    """

    _port = -1  # i2c port
    _address = -1  # i2c address
    _bus = None  # SMBus instance
    _calibrated_t = None  # copreus.baseclasses.CalibratedValue for temperature
    _use_calibration_t = True  # flag - if true, values will be calibrated; if false, values will be returned raw.
    _calibrated_h = None  # copreus.baseclasses.CalibratedValue for humidity
    _use_calibration_h = True  # flag - if true, values will be calibrated; if false, values will be returned raw.
    _calibrated_p = None  # copreus.baseclasses.CalibratedValue for airpressure
    _use_calibration_p = True  # flag - if true, values will be calibrated; if false, values will be returned raw.

    def __init__(self, config, verbose):
        ADriver.__init__(self, config, verbose)
        APolling.__init__(self, config, verbose)

        self._port = self._config["port"]
        self._address = self._config["address"]

        self._use_calibration_t = bool(self._config["use-calibration-temperature"])
        self._calibrated_t = CalibratedValue(self._config["calibration-temperature"], 1)
        self._use_calibration_h = bool(self._config["use-calibration-humidity"])
        self._calibrated_h = CalibratedValue(self._config["calibration-humidity"], 1)
        self._use_calibration_p = bool(self._config["use-calibration-pressure"])
        self._calibrated_p = CalibratedValue(self._config["calibration-pressure"], 1)

    def _poll_device(self):
        """APolling._poll_device"""
        data = bme280_driver.sample(self._bus, self._address)

        t = self._calibrated_t.value(data.temperature, self._use_calibration_t)
        h = self._calibrated_t.value(data.humidity, self._use_calibration_h)
        p = self._calibrated_t.value(data.pressure, self._use_calibration_p)

        self._publish_value(self._topics_pub["temperature"], t)
        self._publish_value(self._topics_pub["humidity"], h)
        self._publish_value(self._topics_pub["pressure"], p)

    def _start_sequence(self):
        """ADriver._start_sequence"""
        self._bus = SMBus(self._port)
        bme280_driver.load_calibration_params(self._bus, self._address)
        self._start_polling()

    def _stop_sequence(self):
        """ADriver._stop_sequence"""
        self._stop_polling()
        self._bus.close()


def standalone():
    """Calls the static method BME_280.standalone()."""
    BME_280.standalone()


if __name__ == "__main__":
    BME_280.standalone()
