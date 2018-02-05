# -*- coding: utf-8 -*-
"""
@author: weber.juche@gmail.com
@time: 2017/1/4 14:10

    “库表元模型”建表函数封装
    ~~~~~~~~~~~~~~~~~~~~~~
"""
import sys
from weberFuncs import PrintTimeMsg,GetCurrentTime,PrettyPrintObj

from cursorFuncs import ProcessCursorTxFunc,DoCreateTablesInDBSchema
#--------------------------------------
def TestCreateTablesExample():
    from testDictParam import ReturnMysqlDictParamDB,ReturnDBSchemaOfTest
    from exampleSchema import ReturnSchemaExample
    dictSchemaExample = ReturnSchemaExample()
    DoCreateTablesInDBSchema(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test",
                             dictSchemaDB=dictSchemaExample)

#--------------------------------------
def testSchemaExampleIDU():
    from CSQLSchema import CSQLSchema
    from testDictParam import ReturnMysqlDictParamDB
    from exampleSchema import ReturnSchemaExample
    dictSchemaExample = ReturnSchemaExample()
    def cbIns(dbConn,conn,cursor):
        o = CSQLSchema(dbConn,conn,cursor,dictSchemaExample)
        dictRet = o.schemaInsertOne('testtab',{
            'opcode': 'opcode1',
            'operst': '0',
            'shapasswd': 'shapasswd',
            'nickname': 'nickname',
            'logincnt': '123',
            'testfloat': '123.34',
        })
        PrettyPrintObj(dictRet,"schemaInsertOne")
        return dictRet.get('errno') == 0

    def cbUpd(dbConn,conn,cursor):
        o = CSQLSchema(dbConn,conn,cursor,dictSchemaExample)
        dictRet = o.schemaUpdateOne('testtab','1',{
            'operst': '1',
            'shapasswd': 'shapasswd7',
            'nickname': 'nickname7',
            'logincnt': '6123',
            'testfloat': '8123.34',
        })
        PrettyPrintObj(dictRet,"schemaUpdateOne")
        return dictRet.get('errno') == 0
    ProcessCursorTxFunc(dictEngine=ReturnMysqlDictParamDB(),
                        sDbName = 'test', #dictSchemaExample.get('dbname','@dbname'),
                        cbDealFunc=cbIns)
                        # cbDealFunc=cbUpd)
#--------------------------------------
if __name__ == '__main__':
    # TestCreateTablesExample()
    testSchemaExampleIDU()
