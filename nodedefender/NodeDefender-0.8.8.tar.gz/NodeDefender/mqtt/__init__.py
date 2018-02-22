import logging
import NodeDefender.mqtt.message
import NodeDefender.mqtt.command
from NodeDefender.mqtt import connection

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

def load(loggHandler):
    logger.addHandler(loggHandler)
    connection.load()
    logger.debug("MQTT Loaded")
    return True
