from sqlitemodel.SQL import SQL
import sqlite3, copy


class Database(object):
    '''Represents an easy to use interface to the database'''

    DatabaseError = sqlite3.DatabaseError
    DB_FILE = None


    def __init__(self, dbfile=None, foreign_keys=False, parse_decltypes=False):
        self.dbfile = dbfile if dbfile else Database.DB_FILE
        self.conn = sqlite3.connect(self.dbfile, detect_types=(sqlite3.PARSE_DECLTYPES if parse_decltypes else 0))
        self.db = self.conn.cursor()
        if(foreign_keys):
            self.db.execute('PRAGMA foreign_keys = ON;')


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


    def close(self):
        if(self.conn):
            self.conn.close();


    def _get_model_column_names(self, model):
        return [n['name'] for n in model.columns()]


    def createTable(self, model):
        sql = SQL().CREATE(model.tablename())
        for column in model.columns():
            sql.COLUMN(column['name'], column['type'])
        with Database() as db:
            db.db.execute(sql.toStr())
            db.conn.commit()


    def save(self, model):
        values = [model.__dict__[i] for i in self._get_model_column_names(model)]
        if(model.id):
            v = ','.join(['%s=?' % i for i in self._get_model_column_names(model)])
            sql = 'UPDATE %s SET %s WHERE rowid=?' % (model.tablename(), v)
            values += [model.id]
        else:
            f = ','.join(self._get_model_column_names(model))
            v = ('?,'*len(self._get_model_column_names(model)))[:-1]
            sql = 'INSERT INTO %s (%s) VALUES (%s)' % (model.tablename(), f, v)
        self.db.execute(sql, values)
        self.conn.commit()
        if(self.db.lastrowid):
            model.id = self.db.lastrowid
        return model.id


    def delete(self, model):
        if(model.id):
            sql = 'DELETE FROM %s WHERE rowid=?;' % model.tablename()
            self.db.execute(sql, (model.id,))
            self.conn.commit()
            return True
        else:
            return False


    def select(self, model, sql, values=()):
        if(sql.__class__ == SQL):
            sql.SELECT().FROM(model.tablename())
            self.db.execute(sql.toStr(), sql.getValues())
        else:
            self.db.execute(sql, values)
        columns = [t[0] for t in self.db.description]
        objects = []
        row = self.db.fetchone()
        mrange = None
        try:
            mrange = xrange
        except:
            mrange = range
        while(row):
            o = copy.deepcopy(model)
            for i in mrange(len(columns)):
                k = 'id' if columns[i] == 'rowid' else columns[i]
                o.__dict__[k]=row[i]
            row = self.db.fetchone()
            objects.append(o)
        return objects


    def selectOne(self, model, sql, values=()):
        res = self.select(model, sql, values)
        return res[0] if len(res) > 0 else None


    def selectById(self, model, id):
        return self.selectOne(model, SQL().WHERE('rowid', '=', id))


    def getRaw(self, sql, values=(), max=-1):
        query = sql.toStr() if sql.__class__ == SQL else sql
        self.db.execute(query, sql.values if sql.__class__ == SQL else values)
        keys = [t[0] for t in self.db.description]
        return (keys, self.db.fetchmany(max))


    def getDict(self, sql, values=(), max=-1):
        header, raw = self.getRaw(sql, values, max)
        table = []
        for row in raw:
            obj = {}
            headIdx = 0
            for name in header:
                obj[name] = row[headIdx]
                headIdx += 1
            table.append(obj)
        return table


    def zeroZero(self, sql, values=()):
        query = sql.toStr() if sql.__class__ == SQL else sql
        self.db.execute(query, sql.values if sql.__class__ == SQL else values)
        row = self.db.fetchone()
        return row[0] if row else -1
