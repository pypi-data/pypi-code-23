from datetime import datetime
import NodeDefender

default_config = {'deployed' : False,
                  'run_mode' : 'TESTING',
                  'key' : 'key',
                  'salt' : 'salt',
                  'host' : '127.0.0.1:5000',
                  'port' : '5000',
                  'self_registration' : True}

config = default_config.copy()

def load_config(parser):
    config['run_mode'] = parser['GENERAL']['RUN_MODE']
    config['key'] = parser['GENERAL']['KEY']
    config['salt'] = parser['GENERAL']['SALT']
    config['host'] = parser['GENERAL']['host']
    config['port'] = int(parser['GENERAL']['port'])
    config['self_registration'] = eval(parser['GENERAL']['SELF_REGISTRATION'])
    NodeDefender.app.config.update(
        RUN_MODE=config['run_mode'],
        SECRET_KEY=config['key'],
        SECRET_SALT=config['salt'])

    if NodeDefender.config.celery.config['enabled']:
        NodeDefender.app.config.update(
            SERVER_NAME=config['host'])

    if config['run_mode'].upper() == 'DEVELOPMENT':
        NodeDefender.app.config.update(DEBUG=True)
    elif config['run_mode'].upper() == 'TESTING':
        NodeDefender.app.config.update(
            DEBUG=True,
            TESTING=True)
    return True

def uptime():
    return str(datetime.now() - NodeDefender.date_loaded)

def set_default():
    config = default_config.copy()
    return True

def set(**kwargs):
    for key, value in kwargs.items():
        if key not in config:
            continue
        NodeDefender.config.general.config[key] = str(value)
    return True

def write():
    config['deployed'] = True
    NodeDefender.config.parser['GENERAL'] = config
    return NodeDefender.config.write()
