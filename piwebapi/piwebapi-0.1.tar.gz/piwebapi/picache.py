import time
import sqlite3 as sqlite


class PICache(object):

    def __init__(self, store='picache.sqlite'):
        """ Create and initialize pi cache """
        self.store = store

        conn = sqlite.connect(self.store)
        # create table
        conn.execute("create table if not exists `picache` (path PRIMARY KEY, value TEXT, expiry INTEGER)")
        conn.close()
        
    def read(self,path):
        """ Read path from cache """
        conn = sqlite.connect(self.store)

        result = conn.execute('SELECT * FROM `picache` WHERE path=?',(path,)).fetchone()

        conn.close()

        if result:
            now = int(time.time())
            # check for expiry
            if result[2] < now:
                self.delete(path)
                return None
            else:
                return result[1]
        else:
            return None
        
    def write(self, path, value, persistence):
        conn = sqlite.connect(self.store)
        timestamp = int(time.time())+persistence
        
        conn.execute('insert or replace into `picache` (path,value,expiry) values (?,?,?)', (path, value, timestamp))

        conn.commit()
        conn.close()

    def delete(self, path):
        conn = sqlite.connect(self.store)
        conn.execute('delete from `picache` where path=?',(path,))
        conn.commit()
        conn.close()

    def clear(self):
        conn = sqlite.connect(self.store)
        conn.execute('delete from `picache`')
        conn.execute('vacuum')
        conn.commit()
        conn.close()
