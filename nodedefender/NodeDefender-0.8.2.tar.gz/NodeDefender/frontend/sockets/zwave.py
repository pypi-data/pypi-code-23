import NodeDefender

def event(mac_address, sensor_id, data):
    NodeDefender.socketio.emit('event', (mac_address, sensor_id, data),
                            namespace='/icpe'+mac_address, broadcast=True)
