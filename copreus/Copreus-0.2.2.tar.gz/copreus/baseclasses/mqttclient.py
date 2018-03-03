import paho.mqtt.client as mqtt
from threading import Event


class MQTTClient(object):
    """Wrapper for the paho.mqtt.client. Used by ADriver and DeviceManager but can also be used for other purposes."""

    client = None  # holds an instance of paho.mqtt.client.Client
    _config = None  # json configuration
    _verbose_mqttclient = False  # print debugging information if set to yes.
    on_message = None  # holds the function that the client uses upon receiving a message from a subscribed channel.
    is_connected = None  # threading.Event - True if connection to mqtt broker has been successfully established.

    def __init__(self, config, verbose):
        self._config = config
        self._verbose_mqttclient = verbose
        self.is_connected = Event()
        self.is_connected.clear()

    def connect(self):
        """Connect to the mqtt broker using the provided configuration and on_message function."""
        if self._verbose_mqttclient:
            print("Connecting to mqtt.")
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(self._config["mqtt-user"], password=self._config["mqtt-password"])
        self.client.connect(self._config["mqtt-address"], self._config["mqtt-port"], 60)
        self.client.loop_start()

    def disconnect(self):
        """Disconnect from mqtt broker and set is_connected to False."""
        self.client.disconnect()
        self.is_connected.clear()

    def _on_connect(self, client, userdata, flags, rc):
        """Return code after trying to connect to mqtt brokder. If successfully connected, is_connected is True."""
        if self._verbose_mqttclient:
            print("Connected with result code " + str(rc))
        if rc == 0:
            self.is_connected.set()

    @staticmethod
    def merge(driver, mqtt_client):
        """Utility method - joins a driver instance with an external mqtt-client. Must be called before connecting."""
        driver._mqtt = mqtt_client
        mqtt_client.on_message = driver._on_message