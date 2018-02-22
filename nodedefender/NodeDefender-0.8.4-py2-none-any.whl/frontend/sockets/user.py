from flask_socketio import emit, send, disconnect, join_room, leave_room, \
        close_room, rooms
import NodeDefender
from flask_login import current_user
from flask import flash, redirect, url_for

def load_sockets(socketio):
    socketio.on_event('create', create, namespace='/user')
    socketio.on_event('info', info, namespace='/user')
    socketio.on_event('groups', groups, namespace='/groups')
    socketio.on_event('update', update, namespace='/user')
    socketio.on_event('name', name, namespace='/user')
    socketio.on_event('role', role, namespace='/user')
    socketio.on_event('freeze', freeze, namespace='/user')
    socketio.on_event('enable', enable, namespace='/user')
    socketio.on_event('resetPassword', reset_password, namespace='/user')
    socketio.on_event('delete', delete, namespace='/user')
    return True

def create(email, firstname, lastname, group = None, role = None):
    if not NodeDefender.db.group.get(group):
        emit('error', ('Group does not exist'), namespace='/general')
        return False

    if NodeDefender.db.user.get(email):
        emit('error', ('User Exists'), namespace='/general')
        return False

    user = NodeDefender.db.user.create(email, firstname, lastname)
    if group:
        NodeDefender.db.group.add_user(group, email)
    if role:
        NodeDefender.db.user.set_role(email, role)
    NodeDefender.mail.user.new_user(user)
    emit('reload', namespace='/general')
    return True

def info(email):
    user = NodeDefender.db.user.get(email)
    if user:
        return emit('info', user.to_json())
    else:
        return emit('error', "User {} not found".format(email),
                    namespace='/general')

def groups(email):
    return emit('groups', NodeDefender.db.user.groups(email))

def update(kwargs):
    NodeDefender.db.user.update(current_user.email, **kwargs)
    emit('reload', namespace='/general')
    return True

def name(email, firstname, lastname):
    NodeDefender.db.user.update(email, **{'firstname' : firstname,
                                          'lastname' : lastname})
    emit('reload', namespace='/general')
    return True

def role(email, role):
    NodeDefender.db.user.set_role(email, role)
    emit('reload', namespace='/general')
    return True

def freeze(email):
    NodeDefender.db.user.disable(email)
    emit('reload', namespace='/general')
    return True

def enable(email):
    NodeDefender.db.user.enable(email)
    emit('reload', namespace='/general')
    return True

def reset_password(email):
    NodeDefender.db.user.reset_password(email)
    emit('reload', namespace='/general')
    return True

def delete(email):
    try:
        NodeDefender.db.user.delete(email)
    except LookupError:
        emit('error')
        return
    url = url_for('admin_view.admin_users')
    emit('redirect', (url), namespace='/general')
