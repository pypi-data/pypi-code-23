from time import sleep

from copreus.baseclasses.adriver import ADriver
from copreus.baseclasses.apolling import APolling
from copreus.baseclasses.aspi import ASPI
from copreus.baseclasses.calibratedvalue import CalibratedValue


class ADC(ADriver, APolling, ASPI):
    """Driver for ADC (analog-digital-converter) that are connected via spi (e.g. TLC548).

    The driver entry in the yaml file consists of:
      * ADriver entries
        * topics_sub: readnow - mqtt-translations.readnow
        * topics_pub: raw (=integer value returned from adc), volt (=converted and calibrated value)
      * APolling entries
      * ASPI entries
      * CalibratedValue entries in a sub-block named 'calibration'
      * ADC own entries are
        * maxvalue: maximum value in volt. result will be normalized towards this value.
        * bit: how many bits are used. typical values are 8, 10, and 12.
        * use-calibration: if set to False, calibration will be ommitted.

    Example:
    device:
        type: adc
        spi:
            pin_cs: 17
            bus: 0
            device: 1
            maxspeed: 500000
        topics-pub:
            raw: /adc/raw
            volt: /adc/volt
        topics-sub:
            readnow: readnow
        mqtt-translations:
            readnow: True
        maxvalue: 24
        bit: 8
        poll-interval: 30
        use-calibration: False
        calibration:
        # - [ref_value, raw_value]
          - [0, 0]
          - [7.2, 6.4]
          - [24, 24]
    """

    _max_value = -1  # maximum value in volt
    _resolution = -1  # 2**bit
    _calibrated_value = None  # copreus.baseclasses.CalibratedValue
    _use_calibration = True  # flag - if true, values will be calibrated; if false, values will be returned raw.

    def __init__(self, config, verbose, spi_lock=None):
        ADriver.__init__(self, config, verbose)
        APolling.__init__(self, config, verbose)
        ASPI.__init__(self, config, verbose, spi_lock)

        self._max_value = float(self._config["maxvalue"])
        self._resolution = 2**int(self._config["bit"])
        self._use_calibration = bool(self._config["use-calibration"])
        self._calibrated_value = CalibratedValue(self._config["calibration"], self._max_value / float(self._resolution))

        self._add_topic_handler(self._topics_sub["readnow"], self._read_now)

    def _read_now(self, msg):
        """on_message handler for topic sub 'readnow'."""
        if self._verbose:
            print("received message '{}' on topic '{}'.".format(msg.payload, msg.topic))
        if str(msg.payload) == str(self._mqtt_translations["readnow"]):
            self._poll_device()
        else:
            raise ValueError("msg.payload expects {}. received '{}' instead.".
                             format(self._mqtt_translations["readnow"], msg.payload))

    def _poll_device(self):
        """APolling._poll_device"""
        self._transfer([0xFF])[0]  # the adc TLC548 has a two step pipeline -> the first read provides the
                                  # value from the last read. this could be a long time ago.
                                  # -> read twice each time -> digitalization and transfer are
                                  # within a guranteed short period.
        sleep(0.01)
        raw = self._transfer([0xFF])[0]
        value = self._calibrated_value.value(raw, self._use_calibration)
        self._publish_value(self._topics_pub["raw"], raw)
        self._publish_value(self._topics_pub["volt"], value)

    def _start_sequence(self):
        """ADriver._start_sequence"""
        self._connect_spi()
        self._subscribe_topics()
        self._start_polling()

    def _stop_sequence(self):
        """ADriver._stop_sequence"""
        self._stop_polling()
        self._unsubscribe_topics()
        self._disconnect_spi()


def standalone():
    """Calls the static method ADC.standalone()."""
    ADC.standalone()


if __name__ == "__main__":
    ADC.standalone()
