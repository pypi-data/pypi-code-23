# -*- coding: utf-8 -*-
"""
@author: weber.juche@gmail.com
@time: 2016/12/30 17:35

    “库表元模型”相关的处理函数，如生成建表语句、生成中间变量等
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from weberFuncs import PrintTimeMsg,GetCurrentTime

def GenListOfCreateSqlFmTab(schemaTable, sEngine, bCommment=True):
    """
        生成某张表的建表语句，包括创建索引语句
        :param schemaTable: “库表元模型” 某张表的定义
        :param sEngine: 数据库类型
        :param bCommment: 是否生成注释
        :return: 建表语句的列表
    """
    def getCrtFieldSQL():
        try:
            if sEngine!="mysql" and sEngine!="sqlite":
                raise Exception("getCrtFieldSQL.sEngine=(%s) not support!" % sEngine)
            dictTypes = { #mysql类型对照关系
                "c":"char", "vc":"varchar", "pwd":"varchar",
                "date":"char", "time":"char",
                "dt":"datetime", "ts":"timestamp",
                "int":"integer",
                "int64":"bigint",
                "byte": "smallint",
                "float": "decimal",
                "text": "text binary",
                "idnew": "integer not null auto_increment PRIMARY key",
                "idval": "integer"
            }
            if sEngine=="Sqlite":
                dictTypes["idnew"] = "integer PRIMARY KEY AUTOINCREMENT"
                dictTypes["text"] = "text"
            sFileldStr = ""
            for dictF in schemaTable["fields"]:
                sType = dictF["type"]
                def getLens():
                    if sType in ["int","int64","byte","text","idnew","idval","dt","ts"]:
                        return ""  # 这些不需要长度
                    else:
                        if sType == "date":
                            return "(8)"
                        if sType == "time":
                            return "(15)"
                        sLens = dictF["lens"]
                        if sType == "float":
                            return "(%s)" % sLens
                        lens = dictF["lens"].split(',')
                        if len(lens)<=0:
                            raise Exception("sType=(%s),lens=(%s)error!" % (sType, lens))
                        return "(%s)" % lens[0] # 其余类型，仅取第一个
                def getNulls():
                    #if not sType in ["c","vc","text"]:
                    #    return "not null"  #这些不能为null
                    if sType in ["dt","ts"]:
                        sLen = dictF.get('lens','')
                        if sLen=='=ins': return '' # 'DEFAULT CURRENT_TIMESTAMP' #
                        if sLen=='=upd': return '' #''DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
                        # WeiYF.20170109 mysql 5.6.4之后版本才同时支持两个时间戳字段
                        # 那就暂时都不支持，由 CSQLSchema 实现。
                        return ''
                    sFlag = dictF.get("flag",'')
                    if 'NULL' in sFlag: # dictF.has_key("initval"):
                        return "null"
                    else:
                        return "not null"
                def getListHint():
                    dictEnum = dictF.get("enum",{})
                    listHint = dictEnum.get("list",[])
                    return ','.join(listHint)
                sOne = "    %s %s%s %s" % (dictF["name"],dictTypes[sType], getLens(), getNulls())
                sHint = getListHint()
                if sHint:
                    if bCommment:
                        sMemo = "  COMMENT '%s: %s'" % (dictF.get("title", ""), sHint)
                    else:
                        sMemo = '  /* %s: %s */' % (dictF.get("title", ""), sHint)
                else:
                    if bCommment:
                        sMemo = "  COMMENT '%s'" % (dictF.get("title", ""))
                    else:
                        sMemo = '  /* %s */' % (dictF.get("title", ""))
                if sFileldStr=="":
                    sFileldStr += "%s%s" % (sOne,sMemo)
                else:
                    sFileldStr += ",\n%s%s" % (sOne,sMemo)
        except KeyError as e:
            PrintTimeMsg("KeyError.e=(%s)" % str(e))
            return ""
        return sFileldStr
    dictSQL = {}
    sTabName = schemaTable["tabname"]
    dictSQL["tabname"] = sTabName
    sTabComment = '%s %s' % (schemaTable.get("tabmemo", ""),schemaTable.get("tabhint", ""))
    if bCommment:
        sMemo1 = ''
        sMemo2 = "  COMMENT '%s'" % (sTabComment)
    else:
        sMemo1 = '  /* %s */' % (sTabComment)
        sMemo2 = ""
    dictSQL["crttab"] = "create table %s (%s\n%s\n)%s; " % (sTabName,sMemo1,getCrtFieldSQL(),sMemo2)
    dictIndex = schemaTable["indexs"]
    listInx = []
    for k,v in sorted(dictIndex.items()):
        sUnique = ""
        if k.startswith('I'):
            sUnique = "unique"
        sOne = "create %s index %s_%s on %s(%s);" % (sUnique,sTabName,k,sTabName,v)
        listInx.append(sOne)
    dictSQL["crtidx"] = listInx
    return dictSQL

def GenerateListOfCreateSqlFmDB(schemaDB, sEngine):
    """
        生成“库表元模型”中多张表的建表语句
        :param schemaDB: “库表元模型” 某张表的定义
        :param sEngine: 数据库类型
        :return: 建表语句的列表
    """
    listCreateSQL = []
    for dictTab in schemaDB["tables"]:
        dictSQL = GenListOfCreateSqlFmTab(dictTab,sEngine)
        listCreateSQL.append(dictSQL['crttab'])
        listCreateSQL.extend(dictSQL['crtidx'])
        listCreateSQL.append('') # 完成一个表多一个空行
    return listCreateSQL


def GenerateCreateSqlFile(schemaDB, sEngine, sTagFN):
    PrintTimeMsg('GenerateCreateSqlFile.Begin...')
    listSQL = GenerateListOfCreateSqlFmDB(schemaDB, sEngine)
    sFNameSQL = 'crt_%s.sql' % sTagFN #schemaDB.get('dbname')
    with open(sFNameSQL,"w") as f: # a=追加模式输出, w=覆盖模式
        for sSQL in listSQL:
            PrintTimeMsg('%s' % sSQL)
            sS = "%s\n" % (sSQL)
            f.write(sS)
        # f.write("\n")
    PrintTimeMsg('GenerateCreateSqlFile.End!!!')

def testExampleCreateTables():
    from exampleSchema import ReturnSchemaExample
    dictSchemaExample = ReturnSchemaExample()
    GenerateCreateSqlFile(dictSchemaExample,'mysql','test')

#--------------------------------------
def TabCalcAssignMiddleVariable(dictSchemaTab, sEngine):
    """
        计算某张表的中间变量并赋值
        :param dictSchemaTab: “库表元模型” 某张表的定义，也作为 MiddleVariable 属性输出变量
        :param sEngine: 数据库类型，备用
        :return: 无
    """
    dictConfig = {}
    dictConfig["sTabName"] = dictSchemaTab["tabname"]
    dictConfig["sFieldId"] = "NULL"
    for k,v in dictSchemaTab["indexs"].items():
        if k=="I0":
            dictConfig["sFieldId"] = v.replace(',','.')
            break
    sListGet = ""
    sListIns = ""
    dictPost = {}
    for dictF in dictSchemaTab["fields"]:
        sName = dictF["name"]
        # sFlag = dictF.get("flag","")
        sType = dictF.get("type","")
        bGet = sType not in ['pwd']
        bIns = sType not in ['idnew']

        sInitVal = dictF.get("initval","")
        if sInitVal:  dictPost[sName] = sInitVal
        else:
            if sType in ('time','dt','ts'):
                sLens = dictF.get("lens","")
                if sLens:  dictPost[sName] = sType+sLens
        if bGet:
            if sListGet: sListGet += ','+sName
            else: sListGet += sName
        if bIns:
            if sListIns: sListIns += ','+sName
            else: sListIns += sName
    dictConfig["sFieldListGet"] = sListGet
    dictConfig["sFieldListIns"] = sListIns
    dictConfig["dictFieldPost"] = dictPost
    dictSchemaTab["MiddleVariable"] = dictConfig
    # return dictConfig

def DbCalcAssignMiddleVariable(dictSchemaDB, sEngine):
    """
        计算某张表的中间变量并赋值
        :param dictSchemaDB: “库表元模型” 的定义，也作为 MiddleVariable 属性输出变量d
        :param sEngine: 数据库类型，备用
        :return: 无
    """
    for dictTab in dictSchemaDB["tables"]:
        TabCalcAssignMiddleVariable(dictTab,sEngine)

def testDbCalcAssignMiddleVariable():
    from weberFuncs import PrettyPrintObj
    from exampleSchema import ReturnSchemaExample
    dictSchemaExample = ReturnSchemaExample()
    DbCalcAssignMiddleVariable(dictSchemaExample,'mysql')
    PrettyPrintObj(dictSchemaExample,"dictSchemaExample")


#--------------------------------------
if __name__ == '__main__':    
    testExampleCreateTables()
    # testDbCalcAssignMiddleVariable()
