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

def DFgetmdbTable(cur,table):
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

def mdbClearTable(cur,table):
    '''deletes table from .mdb'''
    SQL='DELETE FROM '+table+";"
    cur.execute(SQL)#delete current data
    return cur

def DFconcatmdb(cur,table,df):
    '''this function inserts df to table at the end'''
    from pandas import DataFrame
    fn = list(df.columns.values)#field names
    #add brackets around each column:
    fn=["["+v+"]" for v in fn]#this eliminates SQL conflict errors
    ind=list(df.axes[0])
    SQL1=("INSERT INTO "+table+
         str(tuple(fn))+
         " VALUES")
    SQL1=SQL1.replace("'","")
    for i in range(len(ind)):
        SQL2=str(tuple(df.loc[i]))+";"
        SQL2=SQL2.replace(", None",", ''")
        #print(SQL1+SQL2)#for debugging
        cur.execute(SQL1+SQL2)
    return cur

def DFtomdb(cur,table,df):
    '''this function updates a database table with
    the dataframe info'''
    from pandas import DataFrame
    #reset index:
    df.index=[v for v in range(len(df.index.values))]
    cur=mdbClearTable(cur,table)
    cur=DFconcatmdb(cur,table,df)#add new data
    return cur