from flask_socketio import emit, send
import NodeDefender

def load_sockets(socketio):
    socketio.on_event('general', general_info, namespace='/admin')
    socketio.on_event('logging', logging_info, namespace='/admin')
    socketio.on_event('database', database_info, namespace='/admin')
    socketio.on_event('celery', celery_info, namespace='/admin')
    socketio.on_event('mail', mail_info, namespace='/admin')
    socketio.on_event('mqttCreate', create_mqtt, namespace='/admin')
    socketio.on_event('mqttInfo', mqtt_info, namespace='/admin')
    socketio.on_event('mqttDeleteHost', delete_mqtt, namespace='/admin')
    socketio.on_event('mqttUpdateHost', update_mqtt, namespace='/admin')
    socketio.on_event('mqttList', list_mqtt, namespace='/admin')
    return True

def general_info():
    info = {'hostname' : NodeDefender.hostname,
            'release' : NodeDefender.release,
            'date_loaded' : str(NodeDefender.date_loaded),
            'run_mode' : NodeDefender.config.general.run_mode()}
    emit('general', info)
    return True

def logging_info():
    info = {'enabled' : NodeDefender.config.logging.enabled(),
            'type' : NodeDefender.config.logging.type(),
            'name' : NodeDefender.config.logging.name(),
            'server' : NodeDefender.config.logging.server(),
            'port' : NodeDefender.config.logging.port()}
    return emit('logging', info)

def database_info():
    info = {'enabled' : NodeDefender.config.database.enabled(),
            'engine' : NodeDefender.config.database.engine(),
            'server' : NodeDefender.config.database.server(),
            'port' : NodeDefender.config.database.port(),
            'database' : NodeDefender.config.database.db(),
            'file' : NodeDefender.config.database.file()}
    return emit('database', info)

def celery_info():
    info = {'enabled' : NodeDefender.config.celery.enabled(),
            'broker' : NodeDefender.config.celery.broker(),
            'server' : NodeDefender.config.celery.server(),
            'port' : NodeDefender.config.celery.port(),
            'database' : NodeDefender.config.celery.database()}
    return emit('celery', info)

def mail_info():
    info = {'enabled' : NodeDefender.config.mail.enabled(),
            'server' : NodeDefender.config.mail.server(),
            'port' : NodeDefender.config.mail.port(),
            'tls' : NodeDefender.config.mail.tls(),
            'ssl' : NodeDefender.config.mail.ssl(),
            'username' : NodeDefender.config.mail.username(),
            'password' : NodeDefender.config.mail.password()}
    return emit('mail', info)

def create_mqtt(host, port, group):
    try:
        NodeDefender.db.mqtt.create(host, port)
    except AttributeError as e:
        emit('error', e, namespace='/general')
    NodeDefender.db.group.add_mqtt(group, host, port)
    NodeDefender.mail.group.new_mqtt(group, host, port)
    NodeDefender.mqtt.connection.add(host, port)
    emit('reload', namespace='/general')
    return True

def list_mqtt(group):
    emit('list', NodeDefender.db.mqtt.list(group))
    return True

def mqtt_info(host, port):
    mqtt = NodeDefender.db.mqtt.get_redis(host, port)
    sql_mqtt = NodeDefender.db.mqtt.get_sql(host, port)
    mqtt['icpes'] = [icpe.mac_address for icpe in sql_mqtt.icpes]
    mqtt['groups'] = [group.name for group in sql_mqtt.groups]
    emit('mqttInfo', mqtt)
    return True

def update_mqtt(current_host, new_host):
    mqtt = NodeDefender.db.mqtt.get_sql(current_host['host'],
                                        current_host['port'])
    mqtt.host = new_host['host']
    mqtt.port = new_host['port']
    NodeDefender.db.mqtt.save_sql(mqtt)
    emit('reload', namespace='/general')
    return True

def delete_mqtt(host, port):
    NodeDefender.db.mqtt.delete(host, port)
    emit('reload', namespace='/general')
    return True
