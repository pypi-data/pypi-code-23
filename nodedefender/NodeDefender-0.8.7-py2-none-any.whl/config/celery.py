import NodeDefender

default_config = {'enabled' : False,
                  'broker' : '',
                  'host' : '',
                  'port' : '',
                  'database' : ''}

config = default_config.copy()

def load_config(parser):
    config['enabled'] = eval(parser['CELERY']['ENABLED'])
    config['broker'] = parser['CELERY']['BROKER']
    config['host'] = parser['CELERY']['HOST']
    config['port'] = parser['CELERY']['PORT']
    config['database'] = parser['CELERY']['DATABASE']
    NodeDefender.app.config.update(
        CELERY=config['enabled'],
        CELERY_BROKER=config['broker'],
        CELERY_HOST=config['host'],
        CELERY_PORT=config['port'],
        CELERY_DATABASE=config['database'])
    return True

def broker_uri():
    server = config['server']
    port = config['port']
    database = config['database']
    if config['broker'] == 'REDIS':
        return 'redis://'+server+':'+port+'/'+database
    elif config['broker'] == 'AMQP':
        return 'pyamqp://'+server+':'+port+'/'+database
    return None

def set_default():
    config = default_config.copy()
    return True

def set(**kwargs):
    for key, value in kwargs.items():
        if key not in config:
            continue
        NodeDefender.config.celery.config[key] = str(value)

    return True

def write():
    NodeDefender.config.parser['CELERY'] = config
    NodeDefender.config.write()
