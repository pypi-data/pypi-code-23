
# Extensions
from modislock_monitor.extensions import log

# Database
from modislock_monitor.database import Database, Door, DoorStatus
from sqlalchemy.exc import OperationalError, InternalError, IntegrityError

# Pins
from modislock_monitor.platform_detection import isRaspberryPi

# Device
from .base_device import BaseDevice

# GPIO access
if isRaspberryPi:
    import RPi.GPIO as GPIO
else:
    import GPIOEmu as GPIO


class DoorDevice(BaseDevice):
    """Door Sensor

    """
    def __init__(self, device, callback=None):
        assert isinstance(device, Door), 'device needs to be instance of Door'
        super(DoorDevice, self).__init__(device, callback)

        self.device_id = device.iddoor

        if self.pin != 0:
            # Setup Pin
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            # Get Value
            self.current_state = self.STATE_ACTIVE if GPIO.input(self.pin) == GPIO.HIGH else self.STATE_INACTIVE

            # Add event
            GPIO.add_event_detect(self.pin,
                                  GPIO.BOTH,
                                  callback=self.update_state)

        with Database() as db:
            status = db.session.query(DoorStatus).filter(DoorStatus.door_iddoor == self.device_id).first()

            if status is not None:
                status.status = self.current_state

                try:
                    db.session.commit()
                except (IntegrityError, OperationalError, InternalError) as e:
                    db.session.rollback()
                    log.error('Status Monitor Database Error: {}'.format(e.args[0]))
            else:
                door = DoorStatus(status=self.current_state,
                                  door_iddoor=self.device_id)
                db.session.add(door)

                try:
                    db.session.commit()
                except (IntegrityError, OperationalError, InternalError) as e:
                    db.session.rollback()
                    log.error('Status Monitor Database Error: {}'.format(e.args[0]))

    def update_state(self, pin, state=None):
        """Thread worker that watches the door inputs

           Updates the database accordingly.
           :param int gpio_id: GPIO of door that has triggered the event
           :param str state: State manually updated in case of extension system
        """
        if self.pin != 0:
            val = self.STATE_ACTIVE if GPIO.input(self.pin) == GPIO.HIGH else self.STATE_INACTIVE

            if val != self.current_state:
                self.current_state = val
                self.callback(self.device_id, self.current_state)
        else:
            if state is not None:
                if state != self.current_state:
                    self.current_state = state
                    self.callback(self.device_id, self.current_state)

        log.debug('Door Update:\nPin {}/{}\nStatus {}\n'.format(self.pin, self.name, self.current_state))

    def deinitialize(self):
        if self.pin != 0:
            GPIO.remove_event_detect(self.pin)
            GPIO.cleanup(self.pin)
