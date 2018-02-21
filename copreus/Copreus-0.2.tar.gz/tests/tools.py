import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from copreus.baseclasses.mqttclient import MQTTClient

from yaml import load

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import os


def _on_message(client, userdata, msg):
    print(msg.topic, msg.payload)


def resister_to_pubs(filename, pos=None, on_message=None):
    mqtt = MQTTClient(get_mqtt_config(filename), False)
    if on_message is not None:
        mqtt.on_message = on_message
    else:
        mqtt.on_message = _on_message
    mqtt.connect()
    subs = get_topics_pub(filename, pos)
    for k,s in subs.items():
        s = s + "/#"
        print("registering topic '{}'.".format(s))
        mqtt.client.subscribe(s)


def send_to_topic(filename, topic, msg):
    print("sending to topic '{}' the value '{}'".format(topic, msg))
    mqtt = MQTTClient(get_mqtt_config(filename), False)
    mqtt.on_message = _on_message
    mqtt.connect()
    mqtt.client.publish(topic, msg)
    mqtt.disconnect()


def get_mqtt_config(filename):
    config = load(open(filename, 'r'), Loader=Loader)
    credentials = load(open(os.path.expanduser(config["mqtt"]["mqtt-credentials"]), 'r'), Loader=Loader)
    config["mqtt"].update(credentials)
    return config["mqtt"]


def get_mqtt(filename):
    mqtt = MQTTClient(get_mqtt_config(filename), False)
    return mqtt


def get_topics_pub(filename, pos=None):
    c = get_device_config(filename, pos)
    pubs = c["topics-pub"]
    result = {}
    for k,v in pubs.items():
        result[k] = v
    return result


def get_resolution(filename, pos=None):
    c = get_device_config(filename, pos)
    return 2**c["bit"]


def get_maxvalue(filename, pos=None):
    c = get_device_config(filename, pos)
    return c["maxvalue"]


def get_device_config(filename, pos=None):
    config = load(open(filename, 'r'), Loader=Loader)
    if pos is None:
        c = config["device"]
    else:
        c = config["devices"][pos]
    return c


def get_topics_sub(filename, pos=None):
    c = get_device_config(filename, pos)
    subs = c["topics-sub"]
    result = {}
    for k,v in subs.items():
        result[k] = v
    return result


def get_mqtt_translations(filename, pos=None):
    c = get_device_config(filename, pos)
    subs = c["mqtt-translations"]
    return subs


def get_model(filename, pos=None):
    c = get_device_config(filename, pos)
    return str(c["model"])
