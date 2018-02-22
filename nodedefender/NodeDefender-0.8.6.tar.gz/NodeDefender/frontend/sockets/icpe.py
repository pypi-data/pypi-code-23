from flask_socketio import emit, send, disconnect, join_room, leave_room, \
        close_room, rooms
import NodeDefender
from flask_login import current_user

def load_sockets(socketio):
    socketio.on_event('list', list_icpe, namespace='/icpe')
    socketio.on_event('unassigned', unassigned, namespace='/icpe')
    socketio.on_event('info', info, namespace='/icpe')
    socketio.on_event('connection', connection, namespace='/icpe')
    socketio.on_event('power', power, namespace='/icpe')
    socketio.on_event('mqttInclude', include_mode, namespace='/icpe')
    socketio.on_event('mqttExclude', exclude_mode, namespace='/icpe')
    socketio.on_event('mqttUpdate', update_mqtt, namespace='/icpe')
    return True

def online(icpe):
    socketio.emit('info', 'iCPE {} Online'.format(icpe['mac_address']),
         namespace='/general', broadcast=True)
    return True

def offline(icpe):
    socketio.emit('warning', 'iCPE {} Offline'.format(icpe['mac_address']),
         namespace='/general', broadcast=True)
    return True

def list_icpe(node):
    data = {}
    data['node'] = NodeDefender.db.node.get(node).to_json()
    data['icpes'] = [icpe.to_json() for icpe in
                     NodeDefender.db.icpe.list(node)]
    emit('list', data)
    return True

def unassigned():
    icpes = [icpe.mac_address for icpe in
            NodeDefender.db.icpe.unassigned(current_user)]
    emit('unassigned', icpes)
    return True

def info(icpe):
    emit('info', NodeDefender.db.icpe.get(icpe))
    return True

def connection(icpe):
    emit('connection', NodeDefender.icpe.system.network_settings(icpe))
    return True

def power(icpe):
    #emit('power', NodeDefender.icpe.system.battery_info(icpe))
    return True

def include_mode(icpe):
    NodeDefender.mqtt.command.icpe.include_mode(icpe)
    return emit('info', 'Include Mode', namespace='/general')

def exclude_mode(icpe):
    NodeDefender.mqtt.command.icpe.exclude_mode(icpe)
    return emit('info', 'Exclude Mode', namespace='/general')

def update_mqtt(icpe):
    NodeDefender.mqtt.command.icpe.system_info(icpe)
    NodeDefender.mqtt.command.icpe.zwave_info(icpe)
    return emit('info', 'iCPE Updated', namespace='/general')
