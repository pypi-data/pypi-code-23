# -*- coding: utf-8 -*-
"""
@author: weber.juche@gmail.com
@time: 2017/1/3 15:58
    设计并提供“库表元模型”定义示例
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
###########################################################

def ReturnSchemaTest():
    """ 返回 库表元模型 示例 """
    return   {
        "dbname": "dbname",   # 留下数据库参数，方面将来进行数据库属性扩充
        "dbmemo": "例子库",   # 库备注
        "tables": [{
            "tabname": "testtmp",
            "tabmemo": "测试表",
            "fields":[
                { "name":"testid", "type":"int", "lens":"12", "title":"测试标识" },
                { "name":"name", "type":"vc", "lens":"32", "title":"测试名称", "hint":"由英文字母数字和@_符号" },
            ],
            "indexs":{
                "I0":"testid",
            },
        },
        ]
    }

def ReturnDBSchemaOfTest():
    return {
        "dbname": "dbname",   # 留下数据库参数，方面将来进行数据库属性扩充
        "dbmemo": "例子库",   # 库备注
        "tables": [
                {
                "tabname": "testtmp",
                "tabmemo": "测试表",
                "fields":[
                    { "name":"testid", "type":"int", "lens":"12", "title":"测试标识" },
                    { "name":"name", "type":"vc", "lens":"32", "title":"测试名称"},
                ],
                "indexs":{
                    "I0":"testid",
                },
            }
        ]
    }

#--------------------------------------
def testReturnSchemaTest():
    from weberFuncs import PrettyPrintObj
    dictSchemaExample = ReturnSchemaTest()
    PrettyPrintObj(dictSchemaExample,'dictSchemaExample')

def ReturnMysqlDictParamDB():
    # 返回mysql测试用字典参数
    return {  # mysql 数据库引擎的配置
                "engine" : "mysql",     # 数据库引擎类型 mysql sqlite
                "host" : "localhost",   # 主机名
                "port" : 3306,          # 端口号
                # "username" : "mysql",   # 用户名
                # "password" : "mysql",   # 密码
                "username" : "test",   # 用户名
                "password" : "test",   # 密码
                "initcmd" : [           # 初始命令
                    # "set storage_engine=INNODB;",
                    # "SET time_zone = '+8:00';",
                    # "set GLOBAL max_connections=200;",
                    # "set interactive_timeout=24*3600;",
                    "set transaction isolation level read committed;",
                ],
            }

#--------------------------------------
def testReturnDictTest():
    from weberFuncs import PrettyPrintObj
    dictParamDB = ReturnMysqlDictParamDB()
    PrettyPrintObj(dictParamDB,'dictParamDB')
#--------------------------------------
if __name__ == '__main__':    
    testReturnSchemaTest()
    testReturnDictTest()
    
