import uuid
from bson import json_util
from bubot.BujectError import UserError
from bubot.Action import Action
from datetime import datetime


class User:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis
        self.table = 'user'
        self.data = {

        }
    async def auth_by_login(self, login, password):
        res = Action("User.auth_by_login")
        result = await self.db[self.table].find_one({'login': login})
        if not result or result['password'] != password:
            raise UserError('Не правильный логин или пароль.', action=res)

        self.data = result
        user_id = str(result["_id"])
        sessions = await self.redis.hget('users', user_id)
        session_id = str(uuid.uuid4())
        if not sessions:
            sessions = {
                'user': result,
                'sessions': {}
            }
        else:
            sessions = json_util.loads(sessions)
        sessions['sessions'][session_id] = {
            'begin': datetime.now()
        }

        del(result['password'])
        await self.redis.hset('users', user_id, json_util.dumps(sessions))
        return res.set_end({'user_id': user_id,'session_id': session_id})
        # raise HTTPUnauthorized('Не правильный логин или пароль')

    async def check_right(self, user_id, session_id, method=None, method_param=None):
        res = Action('User.check_right')
        sessions = await self.redis.hget('users', user_id)
        if not sessions or session_id not in sessions:
            raise UserError('Не авторизован.', action=res)
        return res.set_end()
