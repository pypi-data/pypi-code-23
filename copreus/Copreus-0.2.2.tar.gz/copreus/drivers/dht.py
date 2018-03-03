import Adafruit_DHT
from copreus.baseclasses.adriver import ADriver
from copreus.baseclasses.apolling import APolling
from copreus.baseclasses.calibratedvalue import CalibratedValue


class DHT(ADriver, APolling):
    """Driver for the DHT temperature/humidity sensor family.

    The driver entry in the yaml file consists of:
      * ADriver entries
        * topics_pub: temperature, humidity
      * APolling entries
      * CalibratedValue entries in a sub-block named 'calibration_temperature'
      * CalibratedValue entries in a sub-block named 'calibration_humidity'
      * DHT entries
        * pin: gpio @ raspberry
        * sensor-type: DHT11, DHT22, AM2302
        * use-calibration_temperature: if set to False, calibration will be ommitted.
        * use-calibration_humidity: if set to False, calibration will be ommitted.

    Example:
    device:
        type: dht
        sensor-type: DHT22
        poll-interval: 30
        pin: 26
        topics-pub:
            temperature: /dht22/temperature/raw
            humidity: /dht22/humidity/raw
        use-calibration-temperature: True
        calibration-temperature:
        # - [ref_value, raw_value]
        use-calibration-humidity: True
        calibration-humidity:
        # - [ref_value, raw_value]
    """

    _pin = -1  # gpio pin id
    _sensor_type = None  # sensor type (one of the values in dict _sensor_type_list)
    _sensor_type_list = {  # list of valid sensor types. the sensor-type entry in yaml must be one of the keys.
        "DHT11": Adafruit_DHT.DHT11,
        "DHT22": Adafruit_DHT.DHT22,
        "AM2302": Adafruit_DHT.AM2302,
    }
    _calibrated_t = None  # copreus.baseclasses.CalibratedValue for temperature
    _use_calibration_t = True  # flag - if true, values will be calibrated; if false, values will be returned raw.
    _calibrated_h = None  # copreus.baseclasses.CalibratedValue for humidity
    _use_calibration_h = True  # flag - if true, values will be calibrated; if false, values will be returned raw.

    def __init__(self, config, verbose):
        ADriver.__init__(self, config, verbose)
        APolling.__init__(self, config, verbose)
        self._pin = self._config["pin"]

        if self._config["sensor-type"] not in self._sensor_type_list.keys():
            raise ValueError("Wrong parameter. Value for 'sensor-type': {} is not in list of accepted values {}.".format(self._config["sensor-type"], self._sensor_type_list.keys()))
        self._sensor_type = self._sensor_type_list[self._config["sensor-type"]]

        self._use_calibration_t = bool(self._config["use-calibration-temperature"])
        self._calibrated_t = CalibratedValue(self._config["calibration-temperature"], 1)
        self._use_calibration_h = bool(self._config["use-calibration-humidity"])
        self._calibrated_h = CalibratedValue(self._config["calibration-humidity"], 1)

    def _poll_device(self):
        """APolling._poll_device"""
        humidity, temperature = None, None
        while humidity is None or temperature is None:
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self._pin)

        t = self._calibrated_t.value(temperature, self._use_calibration_t)
        h = self._calibrated_t.value(humidity, self._use_calibration_h)

        self._publish_value(self._topics_pub["temperature"], t)
        self._publish_value(self._topics_pub["humidity"], h)

    def _start_sequence(self):
        """ADriver._start_sequence"""
        self._start_polling()

    def _stop_sequence(self):
        """ADriver._stop_sequence"""
        self._stop_polling()


def standalone():
    """Calls the static method DHT.standalone()."""
    DHT.standalone()


if __name__ == "__main__":
    DHT.standalone()