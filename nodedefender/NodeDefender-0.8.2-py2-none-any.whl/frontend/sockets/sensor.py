from flask_socketio import emit, send, disconnect, join_room, leave_room, \
        close_room, rooms
import NodeDefender

def load_sockets(socketio):
    socketio.on_event('list', list_sensors, namespace='/sensor')
    socketio.on_event('info', info, namespace='/sensor')
    socketio.on_event('update', update_fields, namespace='/sensor')
    socketio.on_event('mqttUpdate', mqtt_update, namespace='/sensor')
    socketio.on_event('fields', fields, namespace='/sensor')
    socketio.on_event('set', set_sensor, namespace='/sensor')
    socketio.on_event('getParameter', get_parameter, namespace='/sensor')
    socketio.on_event('setParameter', set_parameter, namespace='/sensor')
    return True

def list_sensors(icpe):
    emit('list', NodeDefender.db.sensor.list(icpe))
    return True

def info(icpe, sensor):
    emit('info', NodeDefender.db.sensor.get(icpe, sensor))
    return True

def update_fields(icpe, sensor, kwargs):
    NodeDefender.db.sensor.update(icpe, sensor, **kwargs)
    emit('reload', namespace='/general')
    return True

def mqtt_update(icpe, sensor):
    NodeDefender.mqtt.command.sensor.sensor_info(icpe, sensor)
    emit("info", "Sensor {} Updated".format(sensor), namespace='/general')
    return True

def fields(icpe, sensor):
    emit('fields', NodeDefender.db.sensor.fields(icpe, sensor))
    return True

def set_sensor(mac_address, sensor_id, commandclass, payload):
    NodeDefender.mqtt.command.sensor.set(mac_address, sensor_id, commandclass,
                                         payload = payload)
    return True

def get_parameter(mac_address, sensor_id, number):
    NodeDefender.mqtt.command.sensor.parameter.get(mac_address, sensor_id, number)
    return True

def set_parameter(mac_address, sensor_id, number, size, value):
    NodeDefender.mqtt.command.sensor.parameter.set(mac_address, sensor_id, number,
                                               size, value)
    return True
