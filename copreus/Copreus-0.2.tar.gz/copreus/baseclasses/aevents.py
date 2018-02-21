import RPi.GPIO as GPIO


class AEvents(object):
    """Additional base class for driver that must react to changing pin states.

    Events are registered for BOTH (raising and falling edge). If necessary, the handler function must differentiate
    between raising and falling edge. Usually done by reading the current state of the pin.

    GPIO.setmode(GPIO.BCM)"""

    _events = None  # dict containing the pin-method parings.
    _verbose_avents = False  # print debugging information if set to yes.

    def __init__(self, config, verbose):
        self._events = {}
        self._verbose_avents = verbose
        GPIO.setmode(GPIO.BCM)

    def _add_event(self, pin, func, bounce_time=50):
        """Add an event handler """
        self._events[int(pin)] = {"f": func, "b": bounce_time}

    def _register_events(self):
        """Register all events that are stored in the dict _events. Usually called in the _start_sequence method of the
        silbling."""
        if self._verbose_avents:
            print("register events")
        for pin,event in self._events.items():
            if self._verbose_avents:
                print(" - register event pin:{}, callback:'{}', bounce_time:'{}'".format(str(pin), str(event["f"]), str(event["b"])))
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=event["f"], bouncetime=event["b"])

    def _unregister_events(self):
        """Unregister from all events that are stored in the dict _events. Usually called in the
         _stop_sequence method of the silbling."""
        if self._verbose_avents:
            print("unregister events")
        for pin,event in self._events.items():
            if self._verbose_avents:
                print(" - remove event for pin {}.".format(pin))
            GPIO.remove_event_detect(pin)
