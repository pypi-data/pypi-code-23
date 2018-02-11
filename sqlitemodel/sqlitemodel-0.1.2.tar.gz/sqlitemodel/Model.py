from sqlitemodel.Database import Database


class Model(object):
    '''Abstracts the communication with the database and makes it easy to store objects'''

    def __init__(self, id=None, dbfile=None, foreign_keys=False, parse_decltypes=False):
        self.id = id
        self._dbfile = dbfile
        self.foreign_keys = foreign_keys
        self.parse_decltypes = parse_decltypes
        self.last_error = None


    def columns(self):
        pass


    def tablename(self):
        pass


    def __create_db(self):
        return Database(self._dbfile, foreign_keys=self.foreign_keys, parse_decltypes=self.parse_decltypes)


    def createTable(self):
        with self.__create_db() as db:
            db.createTable(self)


    def save(self):
        with self.__create_db() as db:
            db.save(self)


    def delete(self):
        with self.__create_db() as db:
            return db.delete(self)


    def getModel(self):
        if(self.id):
            with self.__create_db() as m:
                try:
                    model = m.selectById(self, self.id)
                    self.id = model.id
                    for name in m._get_model_column_names(model):
                        self.__dict__[name] = model.__dict__[name]
                except Exception as e:
                    self.last_error = e
                    self.id = None


    def select(self, sql):
        with self.__create_db() as m:
            return m.select(self, sql)


    def selectOne(self, sql):
        with self.__create_db() as m:
            return m.selectOne(self, sql)


    def selectCopy(self, sql):
        '''Run the SQL statement, select the first entry and copy
        the properties of the result object into the calling object.'''
        m = self.selectOne(sql)
        if(m):
            self.id = m.id
            for name in [n['name'] for n in m.columns()]:
                self.__dict__[name] = m.__dict__[name]
