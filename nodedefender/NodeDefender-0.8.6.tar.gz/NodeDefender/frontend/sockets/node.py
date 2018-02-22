from flask_socketio import emit, send, disconnect, join_room, leave_room, \
        close_room, rooms
import NodeDefender
from flask import jsonify, url_for
from geopy.geocoders import Nominatim

def load_sockets(socketio):
    socketio.on_event('create', create, namespace='/node')
    socketio.on_event('delete', delete, namespace='/node')
    socketio.on_event('info', info, namespace='/node')
    socketio.on_event('list', list_icpes, namespace='/node')
    socketio.on_event('addiCPE', add_icpe, namespace='/node')
    socketio.on_event('removeiCPE', remove_icpe, namespace='/node')
    socketio.on_event('location', location, namespace='/node')
    socketio.on_event('update', update, namespace='/node')
    socketio.on_event('updateLocation', update_location, namespace='/node')
    socketio.on_event('coordinates', coordinates, namespace='/node')
    return True

def create(name, group, location):
    NodeDefender.db.node.create(name)
    NodeDefender.db.group.add_node(group, name)
    NodeDefender.db.node.location(name, **location)
    NodeDefender.mail.node.new_node(group, name)
    url = url_for('node_view.nodes_node', name = NodeDefender.serializer.dumps(name))
    emit('redirect', (url), namespace='/general')
    return True

def delete(name):
    NodeDefender.db.node.delete(name)
    url = url_for('node_view.nodes_list')
    emit('redirect', (url), namespace='/general')
    return True

def info(name):
    node = NodeDefender.db.node.get_sql(name)
    node = node.to_json()
    return emit('info', node)

def list_icpes(groups):
    if type(groups) is str:
        groups = [groups]
    nodes = NodeDefender.db.node.list(*groups)
    return emit('list', [node.to_json() for node in nodes])

def add_icpe(node_name, icpe_mac_address):
    try:
        NodeDefender.db.node.add_icpe(node_name, icpe_mac_address)
        emit('reload', namespace='/general')
    except KeyError as e:
        emit('error', e, namespace='/general')
    return True

def remove_icpe(node, mac_address):
    try:
        NodeDefender.db.node.remove_icpe(node_name, icpe_mac_address)
        emit('reload', namespace='/general')
    except KeyError as e:
        emit('error', e, namespace='/general')
    return True

def location(name):
    return emit('location', NodeDefender.db.node.get(name).location.to_json())

def update(name, kwargs):
    node = NodeDefender.db.node.update(name, **kwargs)
    url = url_for('node_view.nodes_node', name = NodeDefender.serializer.dumps(node.name))
    emit('redirect', (url), namespace='/general')
    return True

def update_location(name, location):
    NodeDefender.db.node.location(name, **location)
    return emit('reload', namespace='/general')

def coordinates(street, city):
    geo = Nominatim()
    geocords = geo.geocode(street + ' ' + city)
    if geocords:
        emit('coordinates', (geocords.latitude, geocords.longitude))
    else:
        emit("warning", "Coordinated no found", namespace='/general')
    return True
