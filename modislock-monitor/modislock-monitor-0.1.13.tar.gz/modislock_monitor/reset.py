
from datetime import datetime

# Extensions
from .extensions import log

# Async
from .tasks import system_reset, factory_reset, reboot

# Pins
from .platform_detection import isRaspberryPi

# GPIO access
if isRaspberryPi:
    import RPi.GPIO as GPIO
else:
    import GPIOEmu as GPIO


class Reset(object):
    """Reset Button

    Defines behavior of button presses
    """
    reset_pin = None

    def __init__(self, reset_pin):
        assert type(reset_pin) is int, 'GPIO is not an integer type: %r' % reset_pin
        self.reset_time = datetime.now()
        self.reset_pin = reset_pin

        try:
            GPIO.setup(self.reset_pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF if isRaspberryPi else GPIO.PUD_UP)
        except (RuntimeError, ValueError):
            pass
        else:
            GPIO.add_event_detect(self.reset_pin,
                                  GPIO.BOTH,
                                  callback=self._update_reset_status,
                                  bouncetime=100)

    def _update_reset_status(self, gpio):
        """Thread worker that watches the reset button.

        Has 2 tasks, a short press of less than 30 seconds resets the
        system. A longer than 30 second press resets the system to factory defaults

        :param int gpio: GPIO number

        """
        if gpio != self.reset_pin:
            return

        if GPIO.input(gpio) == GPIO.LOW:
            self.reset_time = datetime.now()
        else:
            seconds_past = (datetime.now() - self.reset_time).total_seconds()
            log.debug('Reset btn held down for {} seconds'.format(seconds_past))

            if seconds_past < 2.0:
                log.info('Resetting controller')
            if 2.0 < seconds_past <= 10.0:
                log.info('Reset Host')
                reboot.delay()
            elif 10.0 < seconds_past <= 30.0:
                log.info('Reset settings in database')
                system_reset.delay()
            elif seconds_past > 30.0:
                log.info('Reset everything to factory')
                factory_reset.delay()
            else:
                self.reset_time = None

    def deinitialize(self):
        """Unregisters the GPIO class used

        :return:
        """
        GPIO.remove_event_detect(self.reset_pin)
        GPIO.cleanup(self.reset_pin)
