import argparse
import os
from pathlib import Path
import copreus.baseclasses.mypyyaml as mypyyaml
from threading import Event, Lock
import RPi.GPIO as GPIO
from copreus.baseclasses.mqttclient import MQTTClient
from copreus.devicemanager.devicefactory import DriverFactory
import copreus

class DeviceManager(object):
    """Takes a yaml config file, creates all devices that are set to active, and starts them.

    The DeviceManager alters the behavior of the devices at three points:
      * A single instance of MQTTClient is provided to all driver.
      * It overrides the individual topic_sub_handler and provides one central _on_message handler.
      * One spi lock is provided to avoid overallocation of the spi interface (Please be note that a single lock is
      used for all spi instances independet of the bus/devices parameter. Thus, even in case of two independent spi
      interfaces only one of them can be used at any given time.)

    See copreus.baseclasses.adriver for a brief description of the yaml config file."""

    _verbose = False  # print debugging information if set to yes
    _config = None  # stores the json config
    _mqtt = None  # instance of MQTTClient
    _topics_sub_handler = None  # mapping between subscribed topic and internal method to handle incoming message
    _devices = None  # list of instantiated devices.
    _is_stopped = None  # threading.Event that is true if the driver is not running. False between start() and stop().
    _spi_lock = None  # threading.Lock

    def __init__(self, config, verbose):
        print("DeviceManager - init")
        self._verbose = verbose
        self._config = config
        if self._verbose:
            print(self._config)

        self._is_stopped = Event()
        self._is_stopped.set()

        self._spi_lock = Lock()

        self._mqtt = MQTTClient(self._config["mqtt"], self._verbose)
        self._mqtt.on_message = self._on_message

        self._topics_sub_handler = {}
        self._devices = []

        for entry in config["devices"]:
            if not entry["active"]:
                continue
            device = DriverFactory.create(entry, verbose, self._spi_lock)
            device._mqtt = self._mqtt
            try:
                for k,v in device._topics_sub_handler.items():
                    self._topics_sub_handler[k] = v
            except AttributeError:
                pass
            self._devices.append(device)
            print(" - added device '{}.{}'".format(device._type, device._name))

    def _on_message(self, client, userdata, msg):
        """Method for mqtt client on_message."""
        self._topics_sub_handler[msg.topic](msg)

    def _start(self):
        """Starts mqtt client and all active devices. _is_stopped is set to False."""
        self._is_stopped.clear()
        self._mqtt.connect()
        self._mqtt.is_connected.wait()
        for device in self._devices:
            device.start()
        print("DeviceManager - started")

    def _stop(self):
        """Stops all devices, disconnects from mqtt and sets _is_stopped to True."""
        for device in self._devices:
            device.stop()
        self._mqtt.disconnect()
        self._is_stopped.set()
        print("DeviceManager - stopped")

    @classmethod
    def _args_to_config(cls, args=None):
        """Handle command line arguments and read the yaml file into a json structure (=config)."""
        desc = "Device Manager\n" \
               "In Greek mythology, Copreus (Κοπρεύς) was King Eurystheus' herald. He announced Heracles' Twelve " \
               "Labors. This script starts severaö device driver on a raspberry pi and connects them to MQTT. " \
               "Thus, copreus takes commands from the king (MQTT) and tells the hero (Device) what its labors " \
               "are. Further, copreus reports to the king whatever the hero has to tell him."
        ap = argparse.ArgumentParser(description=desc)
        ap.add_argument('-c', '--config', type=str, help='yaml config file', required=True)
        ap.add_argument('-v', '--verbose', help='verbose', action="store_true")
        ap.add_argument('--version', action='version',
                            version='%(prog)s {}'.format(copreus.version),
                            help='show the version number and exit')
        if args:
            arguments = vars(ap.parse_args(args))
        else:
            arguments = vars(ap.parse_args())

        verbose = False
        if arguments["verbose"]:
            verbose = True

        config_filename = arguments["config"]
        config_file = Path(config_filename)
        if not config_file.is_file():
            raise FileNotFoundError("config file '{}' not found.".format(config_filename))

        config = mypyyaml.load(open(config_filename, 'r'), Loader=mypyyaml.Loader)
        # config["mqtt"]["mqtt-credentials"] is pointing towards a yaml file (e.g. '~/mqtt_credentials.yaml')
        # the file consists of two entries: mqtt-user and mqtt-password
        credentials = mypyyaml.load(open(os.path.expanduser(config["mqtt"]["mqtt-credentials"]), 'r'),
                                    Loader=mypyyaml.Loader)
        config["mqtt"].update(credentials)

        return config, verbose

    @classmethod
    def standalone(cls, args=None):
        """Public method to start this driver directly. Instantiates an MQTT client and creates an object for the
                given driver."""
        GPIO.setwarnings(False)
        config, verbose = DeviceManager._args_to_config(args)
        config = mypyyaml.dict_deepcopy_lowercase(config)
        dm = DeviceManager(config, verbose)
        dm._start()
        try:
            while not dm._is_stopped.wait(0.1):  # timeout is necessary for CTRL+C
                pass
        except KeyboardInterrupt:
            pass
        dm._stop()


def standalone():
    """Calls the static method DeviceManager.standalone()."""
    DeviceManager.standalone()


if __name__ == "__main__":
    DeviceManager.standalone()
