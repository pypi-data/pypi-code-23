import RPi.GPIO as GPIO

from copreus.baseclasses.adriver import ADriver


class Output(ADriver):
    """Generic driver that sets the given output pin.

    The driver entry in the yaml file consists of:
      * ADriver entries
        * topics_sub: closed - mqtt-translations.closed-true and mqtt-translations.closed-false
      * Output entries
        * pin: gpio pin
        * physical-closed: high/low - mapping between logcial states (closed/open) and physical output
        parameters (low/high)
        * initially-closed: True/False - defines if the output is opened or closed after start of driver

    Example:
    device:
        type: output
        pin: 21
        initially-closed: True
        physical-closed: high
        topics-sub:
            closed: /test/closed
        mqtt-translations:
            closed-true: ON
            closed-false: OFF
    """

    _pin = -1  # gpio pin id
    _gpio_closed = -1  # value to write to gpio pin for closing output (0/1)
    _gpio_opened = -1  # value to write to gpio pin for opening output (0/1)
    _initially_closed = False  # should the output be opened or closed after start

    def __init__(self, config, verbose):
        ADriver.__init__(self, config, verbose)

        self._add_topic_handler(self._topics_sub["closed"], self._message_closed)

        self._pin = int(config["pin"])
        self._initially_closed = bool(config["initially-closed"])
        if str(config["physical-closed"].lower()) == "low":
            self._gpio_closed = 0
        elif str(config["physical-closed"].lower()) == "high":
            self._gpio_closed = 1
        else:
            raise ValueError("'physical-closed' - expected 'low'/'high' but received '{}'.".
                             format(config["physical-closed"].lower()))
        self._gpio_opened = (self._gpio_closed + 1) % 2

    def _message_closed(self, msg):
        """on_message handler for topic sub 'closed'."""
        if self._verbose:
            print("received message '{}' on topic '{}'.".format(msg.payload, msg.topic))
        if str(msg.payload) == str(self._mqtt_translations["closed-true"]):
            if self._verbose:
                print("writing '{}' to pin '{}'.".format(self._gpio_closed, self._pin))
            GPIO.output(self._pin, self._gpio_closed)
        elif str(msg.payload) == str(self._mqtt_translations["closed-false"]):
            if self._verbose:
                print("writing '{}' to pin '{}'.".format(self._gpio_opened, self._pin))
            GPIO.output(self._pin, self._gpio_opened)
        else:
            raise ValueError("Output.'{}'.payload expects {} or {}. received '{}' instead.".format(
                msg.topic, self._mqtt_translations["closed-true"], self._mqtt_translations["closed-false"],
                msg.payload))

    def _start_sequence(self):
        """ADriver._start_sequence"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.OUT)
        if self._initially_closed:
            GPIO.output(self._pin, self._gpio_closed)
        else:
            GPIO.output(self._pin, self._gpio_opened)
        self._subscribe_topics()

    def _stop_sequence(self):
        """ADriver._stop_sequence"""
        self._unsubscribe_topics()
        GPIO.cleanup(self._pin)


def standalone():
    """Calls the static method Output.standalone()."""
    Output.standalone()


if __name__ == "__main__":
    Output.standalone()
