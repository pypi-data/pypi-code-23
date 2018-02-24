import argparse
import os
from threading import Event
from pathlib import Path
import copreus.baseclasses.mypyyaml as mypyyaml
from copreus.baseclasses.mqttclient import MQTTClient
import copreus

class ADriver(object):
    """Base class that all drivers must implement.

     * Provides MQtt-related functionality like subcribe to topics, publish to topics, start/stop mqtt client.
     * start/stop the service.
     * apply basic configuration from json object
     * standalone enabling methods - each driver can be used on its own from the command line.

    A yaml file must contain two root blocks:
     * mqtt - mqtt-address, mqtt-port, and path to credentials file mqtt-credentials (a file consisting of two entries:
     mqtt-user, mqtt-password)
     * device or devices. devices is a list of device entries with two additional parameters per device: active and
     name. a device entry contains at least (driver implementation might add additional ones): type, name, topic-pub
     (list of key/value pairs), topic-sub (list of key/value pairs), and mqtt-translations (what are the
     commands/states-values that are transmitted via mqtt. only where necessary).
    """

    _verbose = False  # print debugging information if set to yes.
    _config = None  # stores the json config
    _topics_pub = None  # list of topics this driver publishes to
    _topics_sub = None  # list of topics this driver listens to
    _topics_sub_handler = None  # mapping between subscribed topic and internal method to handle incoming message
    _mqtt = None  # instance of MQTTClient
    _type = None  # unique identifier of driver class. usually the class name.
    _name = None  # name of driver instance. should be unique in combination with _type.
    _is_stopped = None  # threading.Event that is true if the driver is not running. False between start() and stop().
    _mqtt_translations = None  # contains all mqtt commands/states and their mqtt.payload representations.

    def __init__(self, config, verbose):
        self._verbose = verbose
        self._config = config
        if self._verbose:
            print(self._config)

        self._type = self.__class__.__name__
        if self._type.upper() != self._config["type"].upper():
            raise TypeError("Type of class ({}) is different than type of config ({}).".format(self._type.upper(), self._config["type"].upper()))

        try:
            self._name = self._config["name"]
        except KeyError:
            self._name = self._type

        self._topics_pub = {}
        try:
            for k,v in self._config["topics-pub"].items():
                self._topics_pub[k] = v
        except KeyError:
            pass

        self._topics_sub_handler = {}
        self._topics_sub = {}
        try:
            for k,v in self._config["topics-sub"].items():
                self._topics_sub[k] = v
                self._topics_sub_handler[k] = ADriver._raise_NotImplementedError
        except KeyError:
            pass

        try:
            self._mqtt_translations = {}
            for k, v in self._config["mqtt-translations"].items():
                self._mqtt_translations[k] = str(v).encode('UTF-8')
        except KeyError:
            pass

        self._is_stopped = Event()
        self._is_stopped.set()

    # @abstract
    @staticmethod
    def _raise_NotImplementedError(msg):
        raise NotImplementedError("Please implement method for subscribed topic '{}'.".format(msg.topic))

    def _on_message(self, client, userdata, msg):
        """Method for mqtt client on_message."""
        self._topics_sub_handler[msg.topic](msg)

    def _add_topic_handler(self, topic, function):
        """Add a topic/function pair to the subscription system."""
        self._topics_sub_handler[topic] = function

    def _subscribe_topics(self):
        """Subscribe to all topics that are in dict _topics_sub."""
        if self._verbose:
            print("subscribe topics")
        for k,v in self._topics_sub.items():
            if self._verbose:
                print(" - subscribing to topic '{}'.".format(v))
            self._mqtt.client.subscribe(v)

    def _unsubscribe_topics(self):
        """Unsubscribe from all topics that are in dict _topics_sub."""
        if self._verbose:
            print("unsubscribe topics")
        for k,v in self._topics_sub.items():
            if self._verbose:
                print(" - unsubscribing from topic '{}'.".format(v))
            self._mqtt.client.unsubscribe(v)

    def _publish_value(self, topic, value):
        """Wrapper method to publish a value to the given topic."""
        self._mqtt.client.publish(topic, value)
        if self._verbose:
            print(topic+': '+str(value))

    def start(self):
        """Public method to start the driver. Calls _start_sequence that must be implemented by the silbling."""
        if self._verbose:
            print("start device '{}.{}'.".format(self._type, self._name))
        self._is_stopped.clear()
        self._start_sequence()

    # @abstract
    def _start_sequence(self):
        """This method must be implemented by the silbling class. It should contain everything that must be done
        to start the driver."""
        raise NotImplementedError("Please implement this method!")

    def stop(self):
        """Public method to stop the driver. Calls _stop_sequence that must be implemented by the silbling."""
        if self._verbose:
            print("stop device '{}.{}'.".format(self._type, self._name))
        self._stop_sequence()
        self._is_stopped.set()

    # @abstract
    def _stop_sequence(self):
        """This method must be implemented by the silbling class. It should contain everything that must be done
        to cleanly stop the driver."""
        raise NotImplementedError("Please implement this method!")

    @classmethod
    def _args_to_config(cls, args):
        """Handle command line arguments and read the yaml file into a json structure (=config)."""
        desc = "Device driver for '{}'\n" \
               "In Greek mythology, Copreus (Κοπρεύς) was King Eurystheus' herald. He announced Heracles' Twelve " \
               "Labors. This script starts a device driver on a raspberry pi and connects the device to MQTT. " \
               "Thus, copreus takes commands from the king (MQTT) and tells the hero (Device) what its labors " \
               "are. Further, copreus reports to the king whatever the hero has to tell him.".format(cls.__name__)
        ap = argparse.ArgumentParser(description=desc)
        ap.add_argument('-c', '--config', type=str, help='yaml config file', required=True)
        ap.add_argument('-p', '--pos', type=int, default = -1,
                        help='position in devices list (starts with 0). if not set, a single device '
                             'entry in a block called "device" is assumed.')
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

        pos = arguments["pos"]
        if pos < -1:
            raise SystemExit("'pos' must be a positive integer.")

        return config, verbose, pos

    @classmethod
    def standalone(cls, args=None):
        """Public method to start this driver directly. Instantiates an MQTT client and creates an object for the
        given driver."""
        config, verbose, pos = cls._args_to_config(args)
        config = mypyyaml.dict_deepcopy_lowercase(config)
        config_mqtt = config["mqtt"]
        if pos == -1:
            try:
                config_device = config["device"]
            except KeyError:
                raise SystemExit("No entry 'device' in given config file.")
        else:
            try:
                config_device = config["devices"][pos]
            except KeyError:
                raise SystemExit("No entry found at position {} in block 'devices' in given config file.".format(pos))

        driver = cls(config_device, verbose)
        MQTTClient.merge(driver, MQTTClient(config_mqtt, verbose))
        driver._mqtt.connect()
        driver._mqtt.is_connected.wait()
        driver.start()
        try:
            while not driver._is_stopped.wait(0.1):  # timeout is necessary for CTRL+C
                pass
        except KeyboardInterrupt:
            pass
        driver.stop()
        driver._mqtt.disconnect()


