# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 12:34:41 2018

@author: jticotin

this module contains functions for reading and writing .mdb files
(microsoft access database)


sample script:
MDB = "myfolder/my.mdb"
con,cur=createConn(MDB)
df=getmdbTable(cur,"mytable")
print(df)#display MDB data
cur.close()
con.commit()#save
con.close()


"""

def createConn(MDB,PWD=''):
    '''creates connection to database
    returns con(connection) and cur(cursor)
    example:
    con,cur=createConn("my.mdb")
    #now i'm connected
    cur.close()
    con.commit()#save
    con.close()
    '''
    import pyodbc
    DRV='{Microsoft Access Driver (*.mdb)}'
    # connect to db
    con = pyodbc.connect('DRIVER={};DBQ={};PWD={}'.format(DRV,MDB,PWD))
    cur = con.cursor()
    return con,cur

def getmdbTable(cur,table):
    '''gets table and returns as a list
    note: figure out how to get field names
    it would be better to import as pandas dataframe
    '''
    import pyodbc
    from pandas import DataFrame
    SQL = 'SELECT * FROM '+table+';' # your query goes here
    t = cur.execute(SQL).fetchall()#list with tuples
    t = [list(v) for v in t]#reformat to nested list
    cols = [column[0] for column in cur.description]#get field names
    df=DataFrame(data=t,columns=cols)
    return df
