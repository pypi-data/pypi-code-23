import logging
import NodeDefender

logger = logging.getLogger(__name__)
logger.setLevel('INFO')

def load(loggHandler):
    logger.addHandler(loggHandler)
    icpes = NodeDefender.db.icpe.list()
    for icpe in icpes:
        if NodeDefender.db.icpe.online(icpe.mac_address):
            continue
        NodeDefender.db.icpe.get(icpe.mac_address)
        NodeDefender.mqtt.command.icpe.zwave_info(icpe.mac_address)
        NodeDefender.mqtt.command.icpe.system_info(icpe.mac_address)
        logger.debug("iCPE {} Loaded".fomrmat(icpe.mac_address))
    NodeDefender.icpe.sensor.load(loggHandler)
    logger.info("iCPE Service Loaded")
    return True

from NodeDefender.icpe import zwave, system, sensor, event
