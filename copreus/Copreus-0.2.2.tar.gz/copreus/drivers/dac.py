from copreus.baseclasses.adriver import ADriver
from copreus.baseclasses.aspi import ASPI
from copreus.baseclasses.calibratedvalue import CalibratedValue

class DAC(ADriver, ASPI):
    """Driver for ADC (analog-digital-converter) that are connected via spi (e.g. MCP4922).

    The driver entry in the yaml file consists of:
      * ADriver entries
        * topics_sub: raw (=integer value for the dac), volt (=converted and calibrated value)
      * ASPI entries
      * CalibratedValue entries in a sub-block named 'calibration'
      * ADC own entries are
        * maxvalue: maximum value in volt. volt will be normalized towards this value.
        * bit: how many bits are used. typical values are 8, 10, and 12.
        * use-calibration: if set to False, calibration will be ommitted.
        * config_dac: configuration bit-sequence according to datasheet (0 if none)

    Example:
    device:
        type: dac
        config_dac: 0x3000
        spi:
            pin_cs: 4
            bus: 0
            device: 1
            maxspeed: 500000
        topics-sub:
            raw: /dac/raw
            volt: /dac/volt
        maxvalue: 24
        bit: 12
        use-calibration: True
        calibration:
        # - [ref_value, raw_value]
          - [0.0, 0.0]
          - [7.23, 6.0]
          - [24, 24]
    """

    _max_value = -1  # maximum value in volt
    _config_dac = -1  # configuration bit sequence according to data sheet
    _resolution = -1  # 2**bit
    _calibrated_value = None  # copreus.baseclasses.CalibratedValue
    _use_calibration = True  # flag - if true, values will be calibrated; if false, values will be returned raw.

    def __init__(self, config, verbose, spi_lock=None):
        ADriver.__init__(self, config, verbose)
        ASPI.__init__(self, config, verbose, spi_lock)

        self._config_dac = self._config["config_dac"]

        self._max_value = self._config["maxvalue"]
        self._resolution = 2**int(self._config["bit"])
        self._use_calibration = self._config["use-calibration"]
        self._calibrated_value = CalibratedValue(self._config["calibration"], self._max_value / float(self._resolution))

        self._add_topic_handler(self._topics_sub["raw"], self._write_raw)
        self._add_topic_handler(self._topics_sub["volt"], self._write_volt)

    def _write_raw(self, msg):
        """on_message handler for topic sub 'raw'."""
        if self._verbose:
            print("received message '{}' on topic '{}'.".format(msg.payload, msg.topic))
        self._transfer_raw(int(msg.payload))

    def _write_volt(self, msg):
        """on_message handler for topic sub 'volt'."""
        if self._verbose:
            print("received message '{}' on topic '{}'.".format(msg.payload, msg.topic))
        volt = float(msg.payload)
        raw = self._calibrated_value.raw(volt)
        self._transfer_raw(raw)

    def _transfer_raw(self, raw):
        """Transfer the raw integer value (0<=value<2**bit) to the dac."""
        output = self._config_dac
        if raw > 4095:
            raw = 4095
        if raw < 0:
            raw = 0
        output |= raw
        buf0 = (output >> 8) & 0xff
        buf1 = output & 0xff
        if self._verbose:
            print("sending [{},{}] to dac.".format(buf0, buf1))
        self._transfer([buf0, buf1])

    def _start_sequence(self):
        """ADriver._start_sequence"""
        self._connect_spi()
        self._subscribe_topics()

    def _stop_sequence(self):
        """ADriver._stop_sequence"""
        self._unsubscribe_topics()
        self._disconnect_spi()


def standalone():
    """Calls the static method DAC.standalone()."""
    DAC.standalone()


if __name__ == "__main__":
    DAC.standalone()
