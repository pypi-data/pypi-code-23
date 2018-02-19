#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class CoralResultSet(object):
    """
    Coral Result Set
    Usage:
    >>> rs.toDataFrame()
    """
    def __init__(self, columns=[], values=[]):
        self.columns = columns if columns is not None else []
        self.values = values if values is not None else []
        
    def items(self):
        return [dict(zip(self.columns, v)) for v in self.values]

    def toDataFrame(self):
        """
        toDataFrame: 转换为pandas.DataFrame对象
        :return: DataFrame对象
        """
        import pandas as pd
        df = pd.DataFrame(self.values, columns=self.columns)
        if self.columns and self.columns[0] == 'timestamp':
            df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y%m%d%H%M%S%f")
            df = df.set_index(df['timestamp'])
        return df

    def toCSV(self, *args, **kwargs):
        """
        Write ResultSet to a comma-separated values (csv) file
        Example: rs.toCSV('data.csv', encoding='GBK')
        @see Pandas to_csv()
        :param args: 
        :param kwargs: 
        :return: 
        """
        self.toDataFrame().to_csv(*args, **kwargs)
    
    def __len__(self):
        # if isinstance(self.values, numpy.ndarray):
        #     return self.values.shape[0]
        return len(self.values) if self.values else 0
        
    def __iter__(self):
        return CoralResultSetIterator(self)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [dict(zip(self.columns, row)) for row in self.values[index]]
        else:
            return dict(zip(self.columns, self.values[index]))

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            self.values[index] = [[row.get(name) for name in self.columns] for row in value]
        else:
            self.values[index] = [value.get(name) for name in self.columns]

    def __str__(self, *args, **kwargs):
        return 'CoralResultSet{columns: %s, values: %s}' % (self.columns, self.values)


class CoralResultSetIterator(object):
    def __init__(self, rs):
        self.rs = rs
        self.i = 0
        self.n = len(rs.values)

    def __iter__(self):
        return self

    def next(self):
        if self.i < self.n:
            i = self.i
            self.i += 1
            return dict(zip(self.rs.columns, self.rs.values[i]))
        else:
            raise StopIteration()   


if __name__ == '__main__':
    li = [1, 2, 3]
    print CoralResultSet([], [])
    rs = CoralResultSet(['code', 'name'], [['60000.SH', u'浦发银行'], ['000001.SZ', u'平安银行']])
    print 'rs0 = %s' % rs[0]
    print 'rs0-1 = %s' % rs[0:200]
    rs[0] = {'code': '600001.SH', 'name': 'name1'}
    print 'rs0 = %s' % rs[0]
    rs[0:10] = [{'code': 'code1', 'name': u'浦发银行1'},  {'code': 'code2', 'name': 'name2'}]
    print 'rs0-1 = %s' % rs[0]
    print '-------------'
    print rs
    rs.toCSV('D:/a.csv', encoding='GBK')
    for item in rs:
        print item
