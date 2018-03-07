import urllib.parse
import http.client
import paho.mqtt.client as mqtt

_UNIBOARD_HOST = 'uniboard.io'


def _get_location(url):
    return urllib.parse.urlparse(url)


class UniboardRaspberryPi:
    def __init__(self, token=None):
        self.httpHeaders = {
            'Content-Type': 'application/json'
        }
        self.token = token
        if token:
            self.httpHeaders['X-Uniboard-Token'] = token
        self.httpConn = None
        self.httpsConn = None
        self.mqttConn = None
        self.on_mqtt_connect = None

    def set_token(self, token=None):
        if token:
            self.token = token
            self.httpHeaders['X-Uniboard-Token'] = token

    def http(self, url, data):
        if not url or not data:
            return
        parse_result = _get_location(url)
        if parse_result.scheme == 'http':
            if self.httpConn is None:
                self.httpConn = http.client.HTTPConnection(_UNIBOARD_HOST)
            current_conn = self.httpConn
        elif parse_result.scheme == 'https':
            if self.httpsConn is None:
                self.httpsConn = http.client.HTTPSConnection(_UNIBOARD_HOST)
            current_conn = self.httpsConn
        else:
            return
        current_conn.request('POST', parse_result.path, data, self.httpHeaders)
        return current_conn.getresponse()

    def connect_mqtt(self):
        self.mqttConn = mqtt.Client(client_id=self.token)
        if self.on_mqtt_connect:
            self.mqttConn.on_connect = self.on_mqtt_connect
        self.mqttConn.connect(_UNIBOARD_HOST, 1883)
        self.mqttConn.loop_forever()

    def mqtt(self, topic, data):
        if self.mqttConn is None:
            self.connect_mqtt()
        self.mqttConn.publish(topic, data)
