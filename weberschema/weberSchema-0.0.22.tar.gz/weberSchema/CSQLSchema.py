# -*- coding: utf-8 -*-
"""
@author: weber.juche@gmail.com
@time: 2016/12/30 13:27

    基于“库表元模型”的数据库增删改查操作
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import sys
import time
from weberFuncs import PrintTimeMsg, GetCurrentTime, PrettyPrintObj, GetCurrentTimeMS
from schemaFuncs import DbCalcAssignMiddleVariable
from CSQLQuery import CSQLQuery,getSelectSqlString


def IsValueString(oVal):
    # 判断一个变量是否是 串
    if isinstance(oVal, str):
        return True
    if IsPython3():
        return False
    else:
        if isinstance(oVal, unicode):
            return True
        else:
            return False


# -------------------------------------
def getPercentSignString(listField):
    # 处理百分号
    sSignList = ""
    for field in listField:
        if sSignList=="":
            sSignList += "%s"
        else:
            sSignList += ",%s"
    return sSignList


def getSqlValueTuple(listField, dictFieldPost, dictData):
    # 处理默认值
    listOut = []
    # print 'dictFieldPost',dictFieldPost
    for field in listField:
        sV = dictFieldPost.get(field, "")
        if sV == "":
            sV = dictData.get(field, " ")
        else:
            if sV in ["time=ins","time=upd"]:  # 插入时间或修改时间
                sV = GetCurrentTime()
            elif sV in ["dt=ins","dt=upd","ts=ins","ts=upd"]:  # 插入时间或修改时间
                sV = GetCurrentTimeMS()  # 经测试,使用这种格式化时间才行, 使用time.time()时间戳整数是不行的.
        listOut.append(sV)
    # PrintTimeMsg("getSqlValueTuple=%s=" % listOut)
    return tuple(listOut)


def getUpdSQLStr(sFieldId, dictFieldPost, dictData):
    # 处理update语句
    sUpdOut = ""
    for k,v in dictData.items():
        if k == sFieldId or k in dictFieldPost:
            PrintTimeMsg("Waring: UPDATE field (%s) will be Ignore!" % k)
            continue
        if sUpdOut == "":
            sUpdOut += "%s='%s'" % (k,v)
        else:
            sUpdOut += ",%s='%s'" % (k,v)
    for (k,v) in dictFieldPost.items():
        sV = ''
        if v in ["dt=upd", "ts=upd"]:  # 仅修改时间
            sV = GetCurrentTimeMS()
        elif v in ["time=upd"]:
            sV = GetCurrentTime()
        if sV:
            if sUpdOut == "":
                sUpdOut += "%s='%s'" % (k, sV)
            else:
                sUpdOut += ",%s='%s'" % (k, sV)
    return sUpdOut


def buildCondString(sFieldId, sRestId, dictJSON={}):
    """
       生成单一资源的标识条件串
       sFieldId: 表标识字段
       rest_id: 传入的资源标识取值
    """
    if '.' not in sFieldId:  # 无.表示单一标识
        if IsValueString(sRestId):
            return "%s='%s'" % (sFieldId, sRestId)
        return "%s=%s" % (sFieldId, sRestId)
    listId = sFieldId.split('.')
    sCond = ""
    if dictJSON:
        for n in listId:
            sT = "(%s='%s')" % (n, dictJSON.get(n, n))
            if sCond:
                sCond += " and %s" % sT
            else:
                sCond += sT
    else:
        listVv = sRestId.split('.')
        iLen = len(listId)
        if iLen!=len(listVv):
            PrintTimeMsg("buildCondString.listId=(%s),listVv=(%s)" %(listId, listVv))
            return "0=1"   # 这样就查不到了
        if iLen<=0:
            PrintTimeMsg("buildCondString.listId=(%s).len=%d" %(listId, iLen))
            return "0=2"   # 这样就查不到了
        for i in range(iLen):
            sT = "(%s='%s')" % (listId[i],listVv[i])
            if sCond:
                sCond += " and %s" % sT
            else:
                sCond += sT
    return sCond


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


# -------------------------------------
class CSQLSchema(CSQLQuery):
    # 数据库增删改查操作封装

    def __init__(self,dbConn, conn, cursor, dictSchemaDB):
        """
            :param dbConn: 是 CDBConnection 的实例
            :param conn, cursor 是 CDBCursor with as 返回的游标
            :param dictSchemaDB: “库表元模型”参数定义，取值参见 exampleSchema
        """
        CSQLQuery.__init__(self,dbConn, conn, cursor)
        self.dictSchemaDB = dictSchemaDB
        DbCalcAssignMiddleVariable(self.dictSchemaDB,self.dbConn.getEngine())

    def _getTabSchema(self,sTabName):
        """
           通过表名查找表结构定义
        """
        for d in self.dictSchemaDB["tables"]:
            if d["tabname"] == sTabName: return d
        return {}

    def _getTabMiddleDict(self,sTabName):
        dictTab = self._getTabSchema(sTabName)
        if dictTab:
            return dictTab["MiddleVariable"]
        return {}

    def _getSelectSqlStringDML(self, sTabName, sCond,sOrderBy=""):
        return getSelectSqlString(sTabName, self._getTabMiddleDict(sTabName)["sFieldListGet"], sCond, sOrderBy)

    def schemaSelectOne(self, sTabName, sRestId):
        """
            查询单条记录
            输入参数：
                sTabName: 表名
                sRestId: 资源标识串（一般为整数），多字段联合的话，之间采用.分隔
            输出参数：
                是一个字典形式；示例如下:
                {
                    "errno": 0,   #错误代码，=0表示正确
                    "errmsg":"OK", #错误消息
                    "data": {"fieldname":"value"}  #字典形式数据
                }
                或者
                {
                    "errno": 1064,
                    "errmsg":"You have an error in your SQL syntax"
                }
        """
        sSQL = self._getSelectSqlStringDML(sTabName,
                                           buildCondString(self._getTabMiddleDict(sTabName)["sFieldId"], sRestId))
        lsResult = self.sqlSelectOne(sSQL)
        if lsResult:
            dictDOut = buildSelectDictOut(self._getTabMiddleDict(sTabName)["sFieldListGet"],lsResult)  # self.oCursor.fetchone())
            return {"errno": 0, "errmsg": "SQL=(%s)" % sSQL, "data": dictDOut}
        else:
            return {"errno": 404, "errmsg":"schemaSelectOne(%s) NotFound" % sSQL}

    def schemaQueryCond(self, sTabName,  lsCond=[], lsOrderBy=[], iRowFirst=0, iPageSize=20):
        """
            查询多条记录
            sTabName: 表名
            参见父类 ExecuteQuery() 函数说明
            输入参数：
                sTabName:  表名
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
        return CSQLQuery.ExecuteQuery(self, sTabName,
            self._getTabMiddleDict(sTabName)["sFieldListGet"], lsCond, lsOrderBy, iRowFirst, iPageSize)

    def schemaInsertOne(self, sTabName, dictData):
        """
            插入单条记录
            输入参数：
                sTabName: 表名
                dictData: 字典形式的JSON数据；示例如下：
                {
                    "fieldname1":"value1",
                    "fieldname2":"value2",
                }
            输出参数：
                是一个字典形式；示例如下:
                {
                    "errno":  0,    #错误代码，=0表示正确
                    "errmsg":"OK",  #错误消息
                    "idLast": 10,   #插入数据生成的id
                }
                或者
                {
                    "errno":"1064",
                    "errmsg":"You have an error in your SQL syntax"
                }
        """
        sFieldListIns = self._getTabMiddleDict(sTabName)["sFieldListIns"]
        listField = sFieldListIns.split(',')
        sqlIns = "insert into %s(%s) values (%s) " % (sTabName, sFieldListIns,getPercentSignString(listField))
        # print self._getTabMiddleDict(sTabName)
        lsData = getSqlValueTuple(listField,self._getTabMiddleDict(sTabName)["dictFieldPost"],dictData)
        sSQLHint = '%s,%s' % (sqlIns,str(lsData))
        # PrintTimeMsg("sSQLHint=%s=" % sSQLHint)
        if self.sqlInsertOne(sqlIns,lsData):
            idLast = self.oCursor.lastrowid
            return {"errno":0, "errmsg":"schemaInsertOne(%s) OK" % sSQLHint, "idLast": idLast}
        else:
            return {"errno":401, "errmsg":"schemaInsertOne(%s) Error" % (sSQLHint)}

    def schemaUpdateOne(self, sTabName, sRestId, dictData):
        """
            修改单条记录
            输入参数：
                sTabName: 表名
                sRestId: 资源标识串（一般为整数），多字段联合的话，之间采用.分隔
                dictData: 要修改的字典形式的JSON数据；示例如下：
                {
                    "fieldname1":"value1",
                    "fieldname2":"value2",
                }
            输出参数：
                是一个字典形式；示例如下:
                {
                    "errno":"0",   #错误代码，=0表示正确
                    "errmsg":"OK", #错误消息
                }
                或者
                {
                    "errno":"1064",
                    "errmsg":"You have an error in your SQL syntax"
                }
        """
        sFieldId = self._getTabMiddleDict(sTabName)["sFieldId"]
        dictFieldPost = self._getTabMiddleDict(sTabName)["dictFieldPost"]
        sSQL = "update %s  set %s where %s" % (sTabName,
                    getUpdSQLStr(sFieldId,dictFieldPost,dictData),
                    buildCondString(sFieldId,sRestId))
        # PrintTimeMsg("sSQL=%s=" % sSQL)
        if self.sqlUpdateOne(sSQL):
            return {"errno":0, "errmsg":"sqlUpdateOne(%s) OK" % (sSQL)}
        else:
            return {"errno":402, "errmsg":"sqlUpdateOne(%s) Error" % (sSQL)}

    def schemaDeleteOne(self, sTabName, sRestId):
        """
            删除单条记录
            输入参数：
                sTabName: 表名
                sRestId: 资源标识串（一般为整数），多字段联合的话，之间采用.分隔
            输出参数：
                是一个字典形式；示例如下:
                {
                    "errno":"0",   #错误代码，=0表示正确
                    "errmsg":"OK", #错误消息
                }
                或者
                {
                    "errno":"1064",
                    "errmsg":"You have an error in your SQL syntax"
                }
        """
        sSQL = "delete from %s where %s" % (sTabName,
                buildCondString(self._getTabMiddleDict(sTabName)["sFieldId"],sRestId))
        # PrintTimeMsg("sSQL=%s" % sSQL)
        if self.sqlDeleteOne(sSQL):
            return {"errno":0, "errmsg":"sqlDeleteOne(%s) OK" % (sSQL)}
        else:
            return {"errno":403, "errmsg":"sqlDeleteOne(%s) Error" % (sSQL)}

#--------------------------------------
def TestCSQLSchema():
    from cursorFuncs import ProcessCursorFunc
    from testDictParam import ReturnMysqlDictParamDB,ReturnDBSchemaOfTest
    dictSchemaExample = ReturnDBSchemaOfTest()
    # c = CDBConnDML(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test",dictSchemaDB=dictSchemaExample)
    def cbQuery(dbConn,conn,cursor):
        o = CSQLSchema(dbConn,conn,cursor,dictSchemaExample)
        dictRet = o.schemaSelectOne('testtmp','101')
        PrettyPrintObj(dictRet,"schemaSelectOne.1=")
        dictRet = o.schemaSelectOne('testtmp','1011')
        PrettyPrintObj(dictRet,"schemaSelectOne.2=")

        dictRet = o.schemaQueryCond('testtmp', [],[] )
        PrettyPrintObj(dictRet,"schemaQueryCond.all")
        dictRet = o.schemaQueryCond('testtmp',[['testid','=','100']],[])  # 整数字段可以匹配上字符串
        PrettyPrintObj(dictRet,"schemaQueryCond.found")
        dictRet = o.schemaQueryCond('testtmp',[['testid','=','200']],[])  # 整数字段可以匹配上字符串
        PrettyPrintObj(dictRet,"schemaQueryCond.notfound")

    def cbIDU(dbConn,conn,cursor):
        o = CSQLSchema(dbConn,conn,cursor,dictSchemaExample)
        dictRet = o.schemaInsertOne('testtmp',{
            'testid':'12',
            'name':'name12',
        })
        PrettyPrintObj(dictRet,"schemaInsertOne.dictRet")
        conn.commit()

        dictRet = o.schemaUpdateOne('testtmp', '11', {
            'testid':'11',
            'name':'name11.updA',
        })
        PrettyPrintObj(dictRet,"DoUpdate.dictRet")
        conn.commit()
        # return

        dictRet = o.schemaDeleteOne('testtmp', '12')
        PrettyPrintObj(dictRet,"DoDelete.dictRet")
        # conn.commit()
    # ProcessCursorFunc(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test",cbDealFunc=cbQuery)
    ProcessCursorFunc(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test",cbDealFunc=cbIDU)

def TestCSQLSchemaTx():
    from cursorFuncs import ProcessCursorTxFunc
    from testDictParam import ReturnMysqlDictParamDB,ReturnDBSchemaOfTest
    dictSchemaExample = ReturnDBSchemaOfTest()

    def cbIDU(dbConn,conn,cursor):
        o = CSQLSchema(dbConn,conn,cursor,dictSchemaExample)
        for i in range(5):
            dictRet = o.schemaInsertOne('testtmp',{
                'testid':2000+i,
                'name':'name2000_%s' % i,
            })
            PrettyPrintObj(dictRet,"schemaInsertOne.%s" % i)
            if dictRet.get('errno') != 0:
                return False
        return True

    ProcessCursorTxFunc(dictEngine=ReturnMysqlDictParamDB(),sDbName = "test",cbDealFunc=cbIDU)

#--------------------------------------
if __name__ == '__main__':
    # TestCSQLSchema()
    TestCSQLSchemaTx()

