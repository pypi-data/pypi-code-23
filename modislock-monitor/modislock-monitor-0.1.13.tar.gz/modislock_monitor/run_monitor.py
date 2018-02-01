import sys
import os
import signal
import time

from modislock_monitor.devices import ControllerDevice
from modislock_monitor.extensions import log, mon_config
from modislock_monitor.reset import Reset

# Database
from modislock_monitor.database import Database, Controller, Reader, Door
from sqlalchemy import text

# Pins
from modislock_monitor.platform_detection import isRaspberryPi

# GPIO access
if isRaspberryPi:
    import RPi.GPIO as GPIO
else:
    import GPIOEmu as GPIO


# Inserts module path into system search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def testdb(db):
    """Tests if database connection is valid

    :param Database db: database session
    :return bool: connection succeeded or failed
    """
    try:
        db.session.query("1").from_statement(text("SELECT 1")).all()
        return True
    except:
        return False


def signal_handler(signal, frame):
    """Used to handle termination signals from the OS

    :param signal:
    :param frame:
    :return:
    """
    signals = {2: 'SIGINT', 15: 'SIGTERM'}
    log.info('Monitor stopped with signal: {}'.format(signals[signal]))
    raise ServiceExit


class ServiceExit(Exception):
    """Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


def main():
    log.info('****Monitor Starting***')
    #: Check version of python
    if sys.version_info[:3] < mon_config.REQUIRED_PYTHON_VER:
        log.error("Monitor requires at least Python {}.{}.{}".format(*mon_config.REQUIRED_PYTHON_VER))
        sys.exit(1)

    active_controller = list()

    #: Initialize the GPIO module and PINs
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(mon_config.DEBUG)
    #: Status LED
    GPIO.setup(mon_config.STATUS_PIN, GPIO.OUT, initial=GPIO.LOW)
    reset_btn = Reset(mon_config.RESET_PIN)

    with Database() as db:
        iterations = 0

        while testdb(db) is not True:
            log.debug('Database not available, waiting..')
            time.sleep(2)
            iterations += 1

            if iterations > 20:
                log.error('Database was not available')
                sys.exit(3)

        controller = db.session.query(Controller) \
            .join(Reader, Controller.idcontroller == Reader.controller_idcontroller) \
            .join(Door, Door.controller_idcontroller == Controller.idcontroller) \
            .all()

        if controller is not None:
            for hw in controller:
                try:
                    monitor = ControllerDevice(hw)
                except IOError:
                    pass
                else:
                    log.info('**Controller Started**\n id: {}\nController Name: {}\nPort: {}'.format(monitor.id,
                                                                                                     monitor.name,
                                                                                                     monitor.port))
                    active_controller.append(monitor)

            # Running on PC TEST
            if len(active_controller) is 0 and not isRaspberryPi:
                log.debug('Starting Test Controller Substitution')
                controller[0].port = 'loop://'
                controller[0].name = 'test monitor'
                monitor = ControllerDevice(controller[0])
                active_controller.append(monitor)

        else:
            log.debug('No controllers to start in database')
            sys.exit(2)

    # Registers signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        for monitor in active_controller:
            monitor.start()

        if len(active_controller) > 0:
            while True:
                time.sleep(0.5)
                GPIO.output(mon_config.STATUS_PIN, not GPIO.input(mon_config.STATUS_PIN))
    except (KeyboardInterrupt, ServiceExit):
        reset_btn.deinitialize()
        GPIO.cleanup(mon_config.STATUS_PIN)
    finally:
        # Start threads
        for monitor in active_controller:
            monitor.stop()

        log.info('****Monitor Closing in 5 seconds***')
        time.sleep(5)


if __name__ == '__main__':
    main()
