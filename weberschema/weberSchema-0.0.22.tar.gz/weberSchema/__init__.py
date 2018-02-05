#!/usr/local/bin/python
# -*- coding:utf-8 -*-
"""    
    2017/01/04  Weber Juche
    公共函数 包
"""
from CDBConnection import CDBConnection
from CDBCursor import CDBCursor

from CSQLBase import CSQLBase
from CSQLQuery import CSQLQuery
from CSQLSchema import CSQLSchema

from schemaFuncs import GenerateListOfCreateSqlFmDB,DbCalcAssignMiddleVariable,GenerateCreateSqlFile
from cursorFuncs import CallCursorFunc,ProcessCursorFunc,CallCursorTxFunc,ProcessCursorTxFunc,DoCreateTablesInDBSchema

if __name__ == '__main__':
    pass