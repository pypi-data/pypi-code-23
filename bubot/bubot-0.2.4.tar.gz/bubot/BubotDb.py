from motor.motor_asyncio import AsyncIOMotorClient
from bubot.BujectError import BujectError, TemporaryError
from datetime import datetime


class BubotDb:
    def __init__(self, host):
        self.db = None

    @staticmethod
    def connect():
        client = AsyncIOMotorClient('corp-vnedrenie', 27017)
        db = client.bubot
        return db

    # @staticmethod
    # async def connect2(self, param, loop):
    #     # if not test.env.auth:
    #     #     raise SkipTest('Authentication is not enabled on server')
    #
    #     # self.db is logged in as root.
    #     # await self.db.add_user(param["user"], param["password"])
    #     db = AsyncIOMotorClient(param["host"], param["port"],
    #                             io_loop=loop)[param["db"]]
    #     try:
    #         # Authenticate many times at once to test concurrency.
    #         await asyncio.wait(
    #             [db.authenticate(param["user"], param["password"]) for _ in range(10)],
    #             loop=loop)
    #
    #         # Just make sure there are no exceptions here.
    #         yield from db.remove_user("jesse")
    #         yield from db.logout()
    #         if (yield from at_least(self.cx, (2, 5, 4))):
    #             info = yield from self.db.command("usersInfo", "jesse")
    #             users = info.get('users', [])
    #         else:
    #             users = yield from self.db.system.users.find().to_list(10)
    #
    #         self.assertFalse("jesse" in [u['user'] for u in users])
    #
    #     finally:
    #         yield from remove_all_users(self.db)
    #         test.env.sync_cx.close()

    @staticmethod
    async def begin_processed(db, table, find_id, tz):
        try:
            result = await db[table].update_one(
                {'$and': [
                    find_id,
                    {'$or': [
                        {'processed.begin': {'$exists': False}},
                        {'$where': 'this.processed.end>=this.processed.begin'}
                    ]}
                ]},
                {'$set': {'processed.begin': datetime.now(tz)}})
            if not result.modified_count:
                raise TemporaryError('Уже обновляется')
            return result
        except BujectError as e:
            raise BujectError(e, action_name='BubotDb.begin_processed()')
        except Exception as e:
            raise BujectError(str(e), action_name='BubotDb.begin_processed()')

    @staticmethod
    async def end_processed(db, table, find_id, tz, update_data):
        try:
            update_data['processed.end'] = datetime.now(tz)
        except TypeError:
            update_data = {
                'processed.end': datetime.now(tz),
                'processed.status': 603,
                'processed.msg': 'BubotDB.end_processed() failed'
            }
        result = await db[table].update_one(find_id, {'$set': update_data})
        return result
