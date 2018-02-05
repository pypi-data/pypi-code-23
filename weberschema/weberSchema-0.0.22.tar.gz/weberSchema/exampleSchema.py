# -*- coding: utf-8 -*-
"""
@author: weber.juche@gmail.com
@time: 2016/12/30 13:27

    设计并提供“库表元模型”定义示例
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

版本变更：
    2013年8月 提出数据库表元模型概念，并实现第一版本；
    2016年12月 改造完善实现第二版本；

“库表元模型”指的是，借助字典对象形式，将某个应用的数据库相关表的元数据集中定义；

表schema示例，此文档最新，WeiYF.20130829
schema_db_sample= {
    "dbname": "dbname",   # 留下数据库参数，方面将来进行数据库属性扩充
    "dbmemo": "例子库",   # 库备注
    "tables": [
    {
        "tabname": "example",   # 表名
        "tabmemo": "例子表",    # 表备注
        "fields":[              # 字段列表
            {   # 最完整说明
                "name":"operid",# 字段名
                "type":"idnew", # 字段类型，取值说明
                                # 字符串:c=char,vc=varchar,pwd=vc
                                # 日期时间：date=c(8),time=c(15),dt=datetime,ts=timestamp
                                # 数值：int=integer,byte=sint,float=DECIMAL(12,2),
                                # 文本：text=text,
                                # 标识：新建标识 idnew=serial,关联标识 idval=int
                "lens":"12",    # 长度串，格式：存储长度,显示长度(缺省=存储长度)
                                # 在已知长度的 dt/ts 类型中,用于附加描述其初值 '=ins'=插入时间,'=upd'=修改时间
                "title":"操作员标识", # 显示标题
                "hint":"由系统自动生成", # 录入格式提示,可以没有
                "memo":"用于标识某实体", # 字段含义说明,可以没有，用于进一步描述该字段
                "link":"tab.id", # 关联表字段描述,可以没有
                "enum":{         # 枚举型字段描述，可以没有
                  "kind":"x_LC", # 取值，L=单选，C=多选;
                                 # 采用list来描述后续参数，保持有序状态
                  "list":["A=name_A","B=name_B"]  # 枚举型取值列表说明，建议定义在外面，方便于多处引用
                },
                "initval":"x_val",  # 插入时缺省取值,可以没有
                "flag":"NULL,"      # 英文逗号分隔的标志串
                                    # NULL=表示该字段可以为 null, 默认 not null
            }
        ],
        
        "indexs":{  # 索引列表，I唯一索引,i重复索引
            "I0":"operid",        # I0决定REST服务的资源标识
            "i1":"opcode,operst"  #
        },
        "params":{  #附加参数，可以没有
            "recordnum":"1000",   # 估计记录数
        },
        "MiddleVariable": {     # 存放dbConnection使用的sFieldListGet等中间变量
           "sFieldId":"",       # ID字段名；对于无ID、多字段联合唯一索引，则为'.'分隔开的多个字段;
           "sFieldListGet":"",  # GET返回资源的字段列表，包括ID
           "sFieldListIns":"",  # Insert插入资源的字段列表,允许为空的字段可以不列入
           "dictFieldPost":"",  # POST创建资源的初值字段字典，这些字段无需提供初值;UPDATE修改也不能修改这些字段
        },        
    }
    ],    
}

"""
###########################################################

def ReturnSchemaExample():
    """ 返回 库表元模型 示例 """
    return   {
        "dbname": "dbname",   # 留下数据库参数，方面将来进行数据库属性扩充
        "dbmemo": "例子库",   # 库备注
        "tables": [{
            "tabname": "testtab",
            "tabmemo": "测试表",
            "fields":[
                { "name":"testid", "type":"idnew", "lens":"12", "title":"测试标识" },
                { "name":"opcode", "type":"vc", "lens":"32", "title":"操作员工号", "hint":"由英文字母数字和@_符号" },
                { "name":"operst", "type":"c", "lens":"1,8", "title":"操作员状态","initval":"0",
                  "enum":{ "kind":"L", "list":["0=待改密码","A=正常使用","X=暂停使用"] }   },
                { "name":"shapasswd", "type":"pwd", "lens":"40", "title":"密码", "hint":"SHA算法加密后的密码", "flag":"NULL,"},
                { "name":"nickname", "type":"vc", "lens":"32", "title":"昵称", "hint":"中英文字母数字串", "flag": "NULL," },
                { "name":"logincnt", "type":"int", "lens":"12", "title":"正常登录次数", "memo":"正常登录次数<=0，才可以删除改工号" },
                { "name":"instime", "type":"time", "lens":"=ins", "title":"插入时间", "hint":"注册时间(YYYYMMDD-hhnnss)" },
                { "name":"modtime", "type":"time", "lens":"=upd", "title":"修改时间", "hint":"修改时间(YYYYMMDD-hhnnss)" },
                { "name":"dtins", "type":"dt", "lens":"=ins", "title":"测试插入时间"},
                { "name":"dtupd", "type":"dt", "lens":"=upd", "title":"测试修改时间"},
                { "name":"tsins", "type":"ts", "lens":"=ins", "title":"测试插入时间"},
                { "name":"tsupd", "type":"ts", "lens":"=upd", "title":"测试修改时间"},
                { "name":"testfloat", "type":"float", "lens":"12,4", "title":"测试浮点数"},
            ],
            "indexs":{
                "I0":"testid",
                "I1":"opcode"
            },
        },
        ]
    }

#--------------------------------------
def testReturnSchemaExample():
    from weberFuncs import PrettyPrintObj
    dictSchemaExample = ReturnSchemaExample()
    PrettyPrintObj(dictSchemaExample,'dictSchemaExample')

#--------------------------------------
if __name__ == '__main__':    
    testReturnSchemaExample()
    
