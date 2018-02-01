
# Extensions
from modislock_monitor.extensions import log

# Database
from modislock_monitor.database import Database, Reader
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


class ReaderDevice(BaseDevice):
    """Reader status update

    """

    def __init__(self, device, callback=None):
        assert isinstance(device, Reader), 'device should be of type Reader: %r' % type(device)
        super(ReaderDevice, self).__init__(device, callback)

        self.device_id = device.idreader
        self.__slave_address = device.controller_address
        self.__serial = device.uuid
        self.__software_version = device.software_version

        if self.pin != 0:
            # Setup PIN
            GPIO.setup(self.pin, GPIO.IN)

            # Get initial value
            self.current_state = self.STATE_INACTIVE if GPIO.input(self.pin) == GPIO.LOW else self.STATE_ACTIVE

            # Add event to PIN
            GPIO.add_event_detect(self.pin,
                                  GPIO.BOTH,
                                  callback=self.update_state)

        with Database() as db:
            reader = db.session.query(Reader).filter(Reader.idreader == self.device_id).first()

            if reader is not None:
                reader.status = self.current_state

                try:
                    db.session.commit()
                except (IntegrityError, OperationalError, InternalError) as e:
                    db.session.rollback()
                    log.error('Status Monitor Database Error: {}'.format(e.args[0]))

    def update_state(self, pin, state=None):
        """Thread worker that watches the reader inputs

           Updates the database accordingly.
           :param int gpio_id: GPIO of reader that has triggered the event
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

        log.debug('Reader Update:\nPin {}/{}\nState {}\n'.format(self.pin, self.name, self.current_state))

    @property
    def slave_address(self):
        return self.__slave_address

    @property
    def serial_number(self):
        return self.__serial

    @serial_number.setter
    def serial_number(self, num):
        self.__serial = num

    @property
    def software_version(self):
        return self.__software_version

    @software_version.setter
    def software_version(self, ver):
        self.__software_version = ver

    def deinitialize(self):
        if self.pin != 0:
            GPIO.remove_event_detect(self.pin)
            GPIO.cleanup(self.pin)
