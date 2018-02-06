import mysqlhelper
import hashlib
import random

db=mysqlhelper.helper(host='')

def reg():
    username=input('请输入注册名:')
    userpwd=input('请输入密码:')
    newpwd=hashlib.md5((userpwd+salt).encode('utf-8')).hexdigest()
    result=mysqlhelper.excutesql("insert into s(name,pwd,salt) value ('{0}',{1},'{2}')".format(username,age.pwd))
    if result>0:
        print ('注册成功')
    else:
        print('注册失败')

def Login():
    username = input('请输入登录名')
    userpwd = input('请输入密码')
    db.createconnect()
    result=db.selectdata("select * from s where name='{0}'".format(uesrname))
    if result is not None:
        newpwd = hashlib.md5((userpwd + result[3]).encode('utf-8')).hexdigest()
        if newpwd==result[2]:
            print ('登录成功')
        else:
            print ('密码错误')
    else:
        print ('用户名不存在')