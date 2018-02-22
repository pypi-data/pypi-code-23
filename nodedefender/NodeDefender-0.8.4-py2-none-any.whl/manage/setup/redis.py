from NodeDefender.manage.setup import (manager, print_message, print_topic,
                                       print_info)
from flask_script import prompt
import NodeDefender

@manager.command
def redis():
    print_topic("Redis")
    print_info("Redis is used to store temporary data(Current heat of sensor\
               etc). With redis enabled it will store the data in Redis.\
               Disabled will store in as a local class- object")
    enabled = None
    while enabled is None:
        enabled = prompt("Enable Redis(Y/N)").upper()
        if 'Y' in enabled:
            enabled = True
        elif 'N' in enabled:
            enabled = False
        else:
            enabled = None
    NodeDefender.config.redis.set_config(enabled = enabled)
    if not enabled:
        return True

    host = None
    while host is None:
        host = prompt("Enter Host Address")
    NodeDefender.config.redis.set_config(host = host)

    port = None
    while port is None:
        port = prompt("Enter Server Port")
    NodeDefender.config.redis.set_config(port = port)

    database = ''
    while not database:
        database = prompt("Enter Database")
    NodeDefender.config.redis.set_config(database = database)
    return True
