
import os
from mongoengine import connect

from .. import env
from .unknown_error import UnknownError
from .instance import Instance
from .script_log import ScriptLog


if env.mode in [env.DISTRIBUTED, env.WORK, env.API, env.SCRIPT]:
    if env.configured:
        # 这里不能简单实用 mock 的方式，可能会影响到用户层项目
        connect(
            env.MONGO_CONFIG['db'], host=env.MONGO_CONFIG['host'], port=env.MONGO_CONFIG['port'],
            username=env.MONGO_CONFIG.get('username'), password=env.MONGO_CONFIG.get('password')
        )
    else:
        raise ValueError('must call fastgets.init_fastgets_env to init env')

elif os.environ.get('unittest') == 'true':
    from mongoengine import connection
    from mongomock.mongo_client import MongoClient
    connection.MongoClient = MongoClient
    connect('fastgets')
