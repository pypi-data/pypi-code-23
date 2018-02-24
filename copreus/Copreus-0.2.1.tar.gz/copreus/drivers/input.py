import RPi.GPIO as GPIO

from copreus.baseclasses.adriver import ADriver
from copreus.baseclasses.aevents import AEvents


class Input(ADriver, AEvents):
    """Generic driver that waits for events on the given input pin.

    The driver entry in the yaml file consists of:
      * ADriver entries
        * topics_pub:
          * button_pressed - mqtt-translations.button_pressed
          * button_state - mqtt-translations.button_state-open and mqtt-translations.button_state-closed
      * Input entries
        * pin: gpio pin

    Example:
    device:
        type: input
        pin:  21
        topics-pub:
            button_pressed: /test/button/pressed
            button_state:   /test/button/state
        mqtt-translations:
            button_pressed: PRESSED
            button_state-open: OPEN
            button_state-closed: CLOSED

    """

    _pin = -1  # gpio pin id

    def __init__(self, config, verbose):
        ADriver.__init__(self, config, verbose)
        AEvents.__init__(self, config, verbose)

        self._pin = config["pin"]
        self._add_event(self._pin, self._callback_pin)

    def _callback_pin(self, channel):
        """Event handler for gpio pin 'pin'. Publishes to the topics 'button_state' and 'button_pressed'."""
        state = GPIO.input(self._pin)
        if not state:
            self._publish_value(self._topics_pub["button_pressed"], self._mqtt_translations["button_pressed"])
            self._publish_value(self._topics_pub["button_state"], self._mqtt_translations["button_state-closed"])
        else:
            self._publish_value(self._topics_pub["button_state"], self._mqtt_translations["button_state-open"])


    def _start_sequence(self):
        """ADriver._start_sequence"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self._register_events()

    def _stop_sequence(self):
        """ADriver._stop_sequence"""
        self._unregister_events()
        GPIO.cleanup(self._pin)


def standalone():
    """Calls the static method Input.standalone()."""
    Input.standalone()


if __name__ == "__main__":
    Input.standalone()
