# -*- coding: utf-8 -*-
"""
@author: weber.juche@gmail.com
@time: 2017/1/4 15:08

    数据库SQL语句操作封装
    ~~~~~~~~~~~~~~~~~~~~
"""
import sys
from weberFuncs import PrintTimeMsg,GetCurrentTime,PrettyPrintObj
from CSQLBase import CSQLBase
#--------------------------------------
def getSelectSqlString(sTabName, sFieldListGet, sCond, sOrderBy):
    """
       生成完整Select语句
    """
    sWhere = ""
    if sCond:
        sWhere = "where"
    sql = "select %s from %s %s %s %s" % (sFieldListGet, sTabName, sWhere, sCond, sOrderBy)
    sql = sql.strip()
    PrintTimeMsg("SELECT=(%s)!" % sql)
    return sql

def getQuerySqlWhere(sFieldListGet, lsCond, lsOrderBy):
    """
        生成Query查询语句where子句
    """
    sCond = ""
    for row in lsCond:
        if not row: continue
        if len(row)!=3:
            PrintTimeMsg("lsCond.Warning: len(row)!=3! row=(%s)" % str(row))
            continue
        if not row[0] in sFieldListGet:
            PrintTimeMsg("lsCond.Warning: not in row[0]=(%s)" % row[0])
            continue
        if not row[1].upper() in ['=','<=','<','<>','>','>=','LIKE','IN','BETWEEN']:
            PrintTimeMsg("lsCond.Warning: not in row[1]=(%s)" % row[1])
            continue
        sV = "(%s %s '%s')" % (row[0],row[1],row[2])
        if sCond=="":
            sCond += sV
        else:
            sCond += " and " +sV
    sOrderBy = ""
    sOrderVal = ""
    for row in lsOrderBy:
        if not row: continue
        if len(row)<1:
            PrintTimeMsg("lsOrderBy.Warning: len(row)<1=(%s)" % str(row))
            continue
        if not row[0] in sFieldListGet:
            PrintTimeMsg("lsOrderBy.Warning: not in row[0]=(%s)" % row[0])
            continue
        sAscDesc = ""
        if len(row)==2:
            if not row[1].upper() in ['ASC','DESC']:
                PrintTimeMsg("lsOrderBy.Warning:not in row[1]=(%s)" % row[1])
                continue
            else:
                sAscDesc = row[1]
        sOrderVal += " %s %s " % (row[0],sAscDesc)
    if sOrderVal!="":
        sOrderBy = " order by "+sOrderVal
    return sCond,sOrderBy

def buildSelectDictOut(sFieldListGet, listValue):
    """
       生成Select结果字典
    """
    dictOut = {}
    i = 0
    for n in sFieldListGet.split(','):
        dictOut[n] = listValue[i]
        i += 1
    return dictOut
#--------------------------------------
class CSQLQuery(CSQLBase):
    # 添加数据库查询操作

    def ExecuteQuery(self, sTabName, sFieldListGet, lsCond=[], lsOrderBy=[],iRowFirst=0, iPageSize=20):
        """
            匹配查询多条记录,共享函数
            输入参数：
                sTabName:  表名
                sFieldListGet: 返回字段列表串
                lsCond:  列表形式查询条件参数，空表示全匹配；[(fieldname,op,value)]
                lsOrderBy:  列表形式排序参数，空表示没有要求；[(fieldname,Asc_Desc)]
                iRowFirst: 返回记录起始位置，从0开始
                iPageSize: 每页返回记录数，缺省是20
            输出参数：
                是一个字典形式；示例如下:
                {
                    "errno":"0",   #错误代码，=0表示正确
                    "errmsg":"OK", #错误消息
                    "DebugSQL":"SQL in debug mode",  #调试模式下执行的SQL语句
                    "MatchCnt": 100,  #匹配上的记录数
                    "RowFirst": 20,  #发返回记录起始位置
                    "listData":[{"fieldname":"value"},{"fieldname1":"value1"}]  #列表形式数据
                }
                或者
                {
                    "errno":"1064",
                    "errmsg":"You have an error in your SQL syntax",
                    "DebugSQL":"SQL in debug mode",
                    "listData":[]
                }
        """
        sCond,sOrderBy = getQuerySqlWhere(sFieldListGet,lsCond, lsOrderBy)
        sSQL = getSelectSqlString(sTabName, sFieldListGet, sCond, sOrderBy)
        iMatchCnt = self.oCursor.execute(sSQL)
        if iMatchCnt:
            if iRowFirst>iMatchCnt: iRowFirst=0 # 避免 IndexError: out of range 异常
            self.oCursor.scroll(iRowFirst,mode='absolute')  # execute返回0情况下，会出异常
            if iPageSize>0:
                results=self.oCursor.fetchmany(iPageSize)
            else:
                results=cur.fetchall()
        else:
            results=[]
        lsResult = []
        for lsV in results: # WeiYF.20170104 将列表转化为字典
            lsResult.append(buildSelectDictOut(sFieldListGet,lsV))
        return {
            "errno":0, "errmsg":"Query(%s) OK" % (sCond),
            "DebugSQL": sSQL,
            "MatchCnt": iMatchCnt,
            "RowFirst": iRowFirst,
            "listData": lsResult,
        }

#--------------------------------------
def TestCSQLQuery():
    from cursorFuncs import ProcessCursorFunc
    from testDictParam import ReturnMysqlDictParamDB

    def cbTest(dbConn,conn,cursor):
        o = CSQLQuery(dbConn,conn,cursor)
        dictRet = o.ExecuteQuery('testtmp', 'testid,name', [],[] )
        PrettyPrintObj(dictRet,"dictRet")
    ProcessCursorFunc(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test",cbDealFunc=cbTest)

#--------------------------------------
if __name__ == '__main__':
    TestCSQLQuery()

