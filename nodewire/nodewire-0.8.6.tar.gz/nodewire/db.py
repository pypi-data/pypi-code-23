import asyncio
import json

class db(object):
    def __init__(self, nw):
        self.nw = nw

    async def get(self, table, query):
        '''ahmad = await db.get('test', {'age', 20})'''
        queue = asyncio.Queue()

        def db_result(msg):
            queue.put_nowait(msg.Value)

        self.nw.send('db','get', table, json.dumps(query))
        self.nw.when('db.'+ table, db_result)
        return await queue.get()

    def drop(self, table):
        '''db.drop('test')'''
        self.nw.send('db','set', table, 'drop')

    def remove(self, table, query):
        '''db.remove('test', {'age',40})'''
        self.nw.send('db', 'set', table, 'remove', json.dumps(query))

    def set(self, table, value):
        '''db.set('test', {'name':'ahmad', 'age': 40})'''
        self.nw.send('db', 'set', table, json.dumps(value))

    async def aggregate(self, table, query):
        '''oldest = await db.aggregate('test', [{"$group" : {"_id" : 1, "oldest" : {"$max" : "$age"}}}])'''
        queue = asyncio.Queue()

        def db_result(msg):
            queue.put_nowait(msg.Value)

        self.nw.send('db', 'get', table, 'aggregate', json.dumps(query))
        self.nw.when('db.' + table, db_result)
        return await queue.get()

if __name__ == '__main__':
    from nodewire.control import control
    async def myloop():
        await asyncio.sleep(10)
        mydb = db(ctrl.nw)
        ahmad = await mydb.get('test', {})
        print(ahmad)

    def connected():
        mydb = db(ctrl.nw)
        mydb.set('test', {'name':'ahmad sadiq', 'age': 43})

    ctrl = control()
    ctrl.nw.on_connected = connected
    ctrl.nw.run(myloop())