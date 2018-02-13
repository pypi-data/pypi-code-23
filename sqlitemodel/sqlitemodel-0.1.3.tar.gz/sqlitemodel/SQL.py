class SQL(object):
    '''SQL builder to generate SQL statements'''

    def __init__(self):
        self.__command = None
        self.__select = ''
        self.__update = ''
        self.__delete = ''
        self.__insert = ''
        self.__create = ''
        self.__columns = []
        self.__values = []
        self.values = []
        self.__from = ''
        self.__where = []
        self.__orderBy = ''
        self.__limit = ''


    def CREATE(self, table):
        self.__command = 'create'
        self.__create = 'CREATE TABLE IF NOT EXISTS %s ' % table
        self.__create += '(%s);'
        return self


    def COLUMN(self, name, type):
        self.__columns.append('%s %s' % (name, type))
        return self


    def SELECT(self, *fields):
        self.__command = 'select'
        self.__select = 'SELECT '
        if(fields):
            self.__select += ', '.join(fields)
        else:
            self.__select += 'rowid, *'
        return self


    def UPDATE(self, table):
        self.__command = 'update'
        self.__update = 'UPDATE %s SET ' % table
        return self


    def SET(self, field, value):
        self.__values.append((field, value))
        return self


    def DELETE(self, table):
        self.__command = 'delete'
        self.__delete = 'DELETE FROM %s' % table
        return self


    def INSERT(self, table):
        self.__command = 'insert'
        self.__insert = 'INSERT INTO %s ' % table
        return self


    def VALUES(self, **values):
        self.__values = list({(k, values[k]) for k in values})
        return self


    def FROM(self, table):
        self.__from = ' FROM %s' % table
        return self


    def WHERE(self, field, operator, value, isRaw=False):
        self.__where.append((field, operator, value, isRaw))
        return self


    def AND(self):
        self.__where.append((None, 'AND', None, False))
        return self


    def OR(self):
        self.__where.append((None, 'OR', None, False))
        return self


    def LIMIT(self, offset, max):
        self.__limit = ' LIMIT %s,%s' % (offset, max)
        return self


    def ORDER_BY(self, field, direction):
        self.__orderBy = ' ORDER BY %s %s' % (field, direction)
        return self


    def getValues(self):
        self.toStr()
        return tuple(self.values) if self.values else ();


    def toStr(self):
        sql = None
        where = ''
        if(self.__where):
            where = ' WHERE '
            wherebuild = []
            for t in self.__where:
                if(not t[0] and not t[2]):
                    wherebuild.append(t[1])
                else:
                    wherebuild.append(('%s%s%s' % (t[0], t[1], t[2])) if t[3] else ('%s%s?' % (t[0], t[1])))
            where += ' '.join(wherebuild)

        if(self.__command == 'select'):
            sql = self.__select + self.__from + where + self.__orderBy + self.__limit + ';'
        elif (self.__command == 'insert'):
            sql = self.__insert + '(' + ','.join(['%s' % t[0] for t in self.__values]) + ') VALUES (' + ('?,'*len(self.__values))[:-1] + ');'
            self.values = [t[1] for t in self.__values]
        elif (self.__command == 'update'):
            sql = self.__update + ', '.join(['%s=%s' % (t[0], '?') for t in self.__values]) + where + ';'
            self.values = [t[1] for t in self.__values]
        elif (self.__command == 'delete'):
            sql = self.__delete + where + ';'
            self.values = [t[1] for t in self.__values]
        elif(self.__command == 'create'):
            sql = self.__create % ', '.join(self.__columns)

        if(self.__where):
            self.values = [t[2] for t in self.__where if (t[0] or t[2]) and not t[3]]

        return sql
