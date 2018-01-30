#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import re
import hashlib
import httplib
import urllib
import urllib2
import socket
import StringIO
import json
import gzip
import serialize
import define
import utils
from CoralResultSet import CoralResultSet
# from CoralParallelClient import CoralParallelClient
# from CoralParallelJob import CoralParallelJob

class CoralDBClient(object):
    """
    CoralDB Client
    Usage:
    >>> client = CoralDBClient("coraldb://127.0.0.1:80")
    >>> client.login("test", "123456")
    """
    def __init__(self, address):
        # url = 'coraldb://test:123456@localhost:8086'
        p = re.compile(r"""^coraldb://(([^:]*)?(:[^@]*)?@)?([^:]+):(\d+)$""", re.IGNORECASE)
        m = p.match(address)
        if not m:
            raise Exception('illegal CoralDB address: ' + address)
        self.username = m.group(2)
        self.password = m.group(3)[1:] if m.group(3) else None
        if self.password:
            md5 = hashlib.md5()
            md5.update(self.password)
            self.password = md5.hexdigest()
        self._host = m.group(4)
        self._port = int(m.group(5))
        self._token = None
        self.timeout = 60
        self.compress = False

    def login(self, username=None, password=None):
        """
        login: 登陆
        :param username: 用户名
        :param password: 密码
        :return: None
        :exception: 登陆失败抛出异常
        """
        if username is not None:
            self.username = username
        if password is not None:
            self.password = utils.encodePwd(password)
        params = {'u': self.username, 'p': self.password}
        rep = self.__request('login', params, login=True)
        if rep['error'] == "":
            self._token = rep['token']
        return CoralResultSet()

    def changePwd(self, password):
        """
        changePwd: 修改密码
        :param password: 新密码
        :return: None
        :exception 失败报出异常
        """
        if password is None or password == "":
            raise Exception('new password can not be empty')
        params = {'p': self.password, 'newPwd': password, 'token': self._token}
        self.__request('changePwd', params)
        return CoralResultSet()

    def getTradingDays(self, beginDate=0, endDate=0, market=define.SH):
        """
        getTradingDays: 获取交易日序列
        :param beginDate: 开始日期，默认为系统支持的最早交易日，示例：20161205
        :param endDate: 结束日期，默认为系统支持的最晚交易日，示例：20161206
        :param market: 市场，默认为上海
        :return: 交易日列表
        """
        params = {'beginDate': beginDate, 'endDate': endDate, 'market': market}
        rep = self.__request('getTradingDays', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getStat(self, beginDate=0, endDate=0):
        """
        getStat: 获取数据统计信息
        :param beginDate: 开始日期，默认为系统中存在数据的最早日期，示例：20161205
        :param endDate: 结束日期，默认为系统中存在数据的最晚日期，示例：20161206
        :return: 结果集
        """
        params = {'beginDate': beginDate, 'endDate': endDate}
        rep = self.__request('getStat', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getCode(self, sector='', date=0, fields="*"):
        """
        getCode: 获取系统内置板块信息
        :param sector: 板块名称，多个名称用逗号分隔，默认获取所有板块
        :param date: 数据日期，默认为每只证券最新日期的数据，示例：20161205
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :return: 结果集
        """
        params = {'sector': sector, 'date': date, 'fields': fields}
        rep = self.__request('getCode', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getBar(self, code=[], beginDate=0, endDate=0, cycle=0, fields="*", beginTime=0, endTime=0, holo=False, holoInterval=0):
        """
        getBar: 获取行情数据
        :param code: 证券代码或证券代码列表
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param cycle: 周期，默认为原始数据
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :param beginTime: 开始时间，默认为当天开始，示例：93000
        :param endTime: 结束时间，默认为当天结束，示例：150000
        :param holo: 是否查全息快照表，默认查Level2快照表
        :param holoInterval: 全息快照时间间隔，默认为1000毫秒
        :return: 结果集
        """
        if not code:
            raise Exception("code cannot be empty")
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'code': code, 'beginDate': beginDate, 'endDate': endDate, 'cycle': cycle, 'fields': fields,
                  'beginTime': beginTime, 'endTime': endTime, 'holo': holo, 'holoInterval': holoInterval}
        rep = self.__request('getBar', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getOrder(self, code=[], beginDate=0, endDate=0, fields="*", beginTime=0, endTime=0):
        """
        getOrder: 获取逐笔委托数据
        :param code: 证券代码或证券代码列表
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :param beginTime: 开始时间，默认为当天开始，示例：93000
        :param endTime: 结束时间，默认为当天结束，示例：150000
        :return: 结果集
        """
        if not code:
            raise Exception("code cannot be empty")
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'code': code, 'beginDate': beginDate, 'endDate': endDate, 'fields': fields,
                  'beginTime': beginTime, 'endTime': endTime}
        rep = self.__request('getOrder', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getKnock(self, code=[], beginDate=0, endDate=0, fields="*", beginTime=0, endTime=0):
        """
        getOrder: 获取逐笔委托数据
        :param code: 证券代码或证券代码列表
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :param beginTime: 开始时间，默认为当天开始，示例：93000
        :param endTime: 结束时间，默认为当天结束，示例：150000
        :return: 结果集
        """
        if not code:
            raise Exception("code cannot be empty")
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'code': code, 'beginDate': beginDate, 'endDate': endDate, 'fields': fields,
                  'beginTime': beginTime, 'endTime': endTime}
        rep = self.__request('getKnock', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserData(self, table, query="", sort="", fields="*", offset=0, limit=0, password=""):
        """
        getUserData: 查询用户数据
        :param table: 数据表名
        :param query: 查询条件，示例：{"name": "foo", "age": {"$gt": 18}}
        :param sort: 排序条件，示例：name,-age
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :param offset: 偏移量，默认为0
        :param limit: 查询结果数量限制，默认无限制
        :param password: 访问密码，访问其他人的数据时需要填写
        :return: 结果集
        """
        if not table:
            raise Exception("table is required")
        query = json.dumps(query) if query else ""
        if password:
            password = utils.encodePwd(password)
        params = {'table': table, 'query': query, 'sort': sort, 'fields': fields, 'offset': offset, 'limit': limit, 'password': password}
        ret = []
        if limit <= 0:
            _offset = offset
            _limit = 10000
            while True:
                params['offset'] = _offset
                params['limit'] = _limit
                rep = self.__request('getUserData', params)
                rows = rep['data']
                ret.extend(rows)
                _offset += _limit
                if len(rows) < _limit:
                    break
        else:
            rep = self.__request('getUserData', params)
            ret = rep['data']
        return ret

    def listUserData(self):
        """
        listUserData: 查看当前用户数据信息
        :return:
        """
        rep = self.__request('listUserData')
        return CoralResultSet(rep['columns'], rep['values'])

    def setUserData(self, table, query="", data=[], password=""):
        """
        setUserData: 保存或更新用户数据
        :param table: 数据表名
        :param query: 查询条件，示例：{"name": "foo", "age": {"$gt": 18}}
        :param data: 待保存的数据或列表
        :param password: 访问密码，访问其他人的数据时需要填写
        :return:
        """
        if not table:
            raise Exception("table is required")
        if not data:
            raise Exception("data is required")
        if query:
            if isinstance(data, list):
                raise Exception('data cannot be a list when query is not empty')
        else:
            data = data if isinstance(data, list) else [data]
        query = json.dumps(query) if query else ""
        data = json.dumps(data) if data else ""
        if password:
            password = utils.encodePwd(password)
        body = {'table': table, 'query': query, 'data': data, 'password': password}
        body = json.dumps(body)
        self.__request('setUserData', data=body)

    def delUserData(self, table, query="", password=""):
        """
        delUserData: 删除用户数据
        :param table: 数据表名
        :param query: 查询条件，示例：{"name": "foo", "age": {"$gt": 18}}
        :param password: 访问密码，访问其他人的数据时需要填写
        :return:
        """
        if not table:
            raise Exception("table is required")
        query = json.dumps(query) if query else ""
        if password:
            password = utils.encodePwd(password)
        params = {'table': table, 'query': query, 'password': password}
        self.__request('delUserData', params)

    def setUserDataIndex(self, table, index=[], password=""):
        """
        setUserDataIndex: 设置用户数据索引
        :param table: 数据表名
        :param index: 索引，为空表示删除所有索引，示例：["date,fund_id", "code", "market"]
        :param password: 访问密码，访问其他人的数据时需要填写
        :return:
        """
        if not table:
            raise Exception("table is required")
        index = ';'.join(index if isinstance(index, list) else [index])
        if password:
            password = utils.encodePwd(password)
        params = {'table': table, 'index': index, 'password': password}
        self.__request('setUserDataIndex', params)

    def setUserDataPassword(self, table, roPassword="", rwPassword=""):
        """
        setUserDataPassword: 设置用户数据访问密码
        :param table: 数据表名
        :param roPassword: 只读访问密码，为空表示禁用
        :param rwPassword: 读写访问密码，为空表示禁用
        :return:
        """
        if not table:
            raise Exception("table is required")
        params = {'table': table, 'roPassword': roPassword, 'rwPassword': rwPassword}
        self.__request('setUserDataPassword', params)

    def getUserSpotAsset(self, beginDate=0, endDate=0, fundId=[], username=[]):
        """
        getUserSpotAsset: 获取用户现货资金
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fundId: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username}
        rep = self.__request('getUserSpotAsset', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserSpotPosition(self, beginDate=0, endDate=0, fundId=[], username=[], code=[]):
        """
        getUserSpotPosition: 获取用户现货持仓
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fundId: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :param code: 代码，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username, 'code': code}
        rep = self.__request('getUserSpotPosition', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserSpotOrder(self, beginDate=0, endDate=0, fundId=[], username=[], code=[], bsFlag=[], orderNo=[]):
        """
        getUserSpotOrder: 获取用户现货委托
        :param date: 日期，示例：20161205
        :param fund_id: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :param code: 代码，默认为所有
        :param bsFlag: 买卖标记（1-买入，2-卖出，3-申购，4-赎回），默认为所有
        :param orderNo: 委托合同号，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        code = ','.join(code if isinstance(code, list) else [code])
        bsFlag = ','.join(bsFlag if isinstance(bsFlag, list) else [bsFlag])
        orderNo = ','.join(orderNo if isinstance(orderNo, list) else [orderNo])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username, 'code': code,
                  'bsFlag': bsFlag, 'orderNo': orderNo}
        rep = self.__request('getUserSpotOrder', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserSpotKnock(self, beginDate=0, endDate=0, fundId=[], username=[], code=[], bsFlag=[], matchType=[], orderNo=[]):
        """
        getUserSpotKnock: 获取用户现货成交
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fundId: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :param code: 代码，默认为所有
        :param bsFlag: 买卖标记（1-买入，2-卖出，3-申购，4-赎回），默认为所有
        :param matchType: 成交类型（1-成交，2-撤单，3-废单），默认为所有
        :param orderNo: 委托合同号，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        code = ','.join(code if isinstance(code, list) else [code])
        bsFlag = ','.join(bsFlag if isinstance(bsFlag, list) else [bsFlag])
        matchType = ','.join(matchType if isinstance(matchType, list) else [matchType])
        orderNo = ','.join(orderNo if isinstance(orderNo, list) else [orderNo])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username, 'code': code,
                  'matchType': matchType, 'orderNo': orderNo}
        rep = self.__request('getUserSpotKnock', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserFutureAsset(self, beginDate=0, endDate=0, fundId=[], username=[]):
        """
        getUserFutureAsset: 获取用户期货资金
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fundId: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username}
        rep = self.__request('getUserFutureAsset', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserFuturePosition(self, beginDate=0, endDate=0, fundId=[], username=[], hedgeFlag=0, code=[]):
        """
        getUserFuturePosition: 获取用户期货持仓
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fundId: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :param hedgeFlag: 套保标记（1-投机，2-套利，3-套保），默认为所有
        :param code: 代码，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username,
                  'hedgeFlag': hedgeFlag, 'code': code}
        rep = self.__request('getUserFuturePosition', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserFutureOrder(self, beginDate=0, endDate=0, fundId=[], username=[], hedgeFlag=0, code=[], bsFlag=[], orderNo=[]):
        """
        getUserFutureOrder: 获取用户期货委托
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fundId: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :param hedgeFlag: 套保标记（1-投机，2-套利，3-套保），默认为所有
        :param code: 代码，默认为所有
        :param bsFlag: 买卖标记（1-买入，2-卖出，3-申购，4-赎回），默认为所有
        :param orderNo: 委托合同号，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        code = ','.join(code if isinstance(code, list) else [code])
        bsFlag = ','.join(bsFlag if isinstance(bsFlag, list) else [bsFlag])
        orderNo = ','.join(orderNo if isinstance(orderNo, list) else [orderNo])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username,
                  'hedgeFlag': hedgeFlag, 'code': code, 'bsFlag': bsFlag, 'orderNo': orderNo}
        rep = self.__request('getUserFutureOrder', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserFutureKnock(self, beginDate=0, endDate=0, fundId=[], username=[], hedgeFlag=0, code=[], bsFlag=[], matchType=[], orderNo=[]):
        """
        getUserFutureKnock: 获取用户期货成交
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fundId: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :param hedgeFlag: 套保标记（1-投机，2-套利，3-套保），默认为所有
        :param code: 代码，默认为所有
        :param bsFlag: 买卖标记（1-买入，2-卖出，3-申购，4-赎回），默认为所有
        :param matchType: 成交类型（1-成交，2-撤单，3-废单），默认为所有
        :param orderNo: 委托合同号，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        code = ','.join(code if isinstance(code, list) else [code])
        bsFlag = ','.join(bsFlag if isinstance(bsFlag, list) else [bsFlag])
        matchType = ','.join(matchType if isinstance(matchType, list) else [matchType])
        orderNo = ','.join(orderNo if isinstance(orderNo, list) else [orderNo])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username,
                  'hedgeFlag': hedgeFlag, 'code': code, 'bsFlag': bsFlag, 'matchType': matchType, 'orderNo': orderNo}
        rep = self.__request('getUserFutureKnock', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserOptionAsset(self, beginDate=0, endDate=0, fundId=[], username=[]):
        """
        getUserOptionAsset: 获取用户期权资金
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fundId: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username}
        rep = self.__request('getUserOptionAsset', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserOptionPosition(self, beginDate=0, endDate=0, fundId=[], username=[], code=[]):
        """
        getUserOptionPosition: 获取用户期权持仓
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fundId: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :param code: 代码，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username, 'code': code}
        rep = self.__request('getUserOptionPosition', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserOptionOrder(self, beginDate=0, endDate=0, fundId=[], username=[], code=[], bsFlag=[], orderNo=[]):
        """
        getUserOptionOrder: 获取用户期权委托
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fundId: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :param code: 代码，默认为所有
        :param bsFlag: 买卖标记（1-买入，2-卖出，3-申购，4-赎回），默认为所有
        :param orderNo: 委托合同号，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        code = ','.join(code if isinstance(code, list) else [code])
        bsFlag = ','.join(bsFlag if isinstance(bsFlag, list) else [bsFlag])
        orderNo = ','.join(orderNo if isinstance(orderNo, list) else [orderNo])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username,
                  'code': code, 'bsFlag': bsFlag, 'orderNo': orderNo}
        rep = self.__request('getUserOptionOrder', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getUserOptionKnock(self, beginDate=0, endDate=0, fundId=[], username=[], code=[], bsFlag=[], matchType=[], orderNo=[]):
        """
        getUserOptionKnock: 获取用户期权成交
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fundId: 资金账号，默认为所有
        :param username: 用户名，默认为所有
        :param code: 代码，默认为所有
        :param bsFlag: 买卖标记（1-买入，2-卖出，3-申购，4-赎回），默认为所有
        :param matchType: 成交类型（1-成交，2-撤单，3-废单），默认为所有
        :param orderNo: 委托合同号，默认为所有
        :return:
        """
        fundId = ','.join(fundId if isinstance(fundId, list) else [fundId])
        username = ','.join(username if isinstance(username, list) else [username])
        code = ','.join(code if isinstance(code, list) else [code])
        bsFlag = ','.join(bsFlag if isinstance(bsFlag, list) else [bsFlag])
        matchType = ','.join(matchType if isinstance(matchType, list) else [matchType])
        orderNo = ','.join(orderNo if isinstance(orderNo, list) else [orderNo])
        params = {'beginDate': beginDate, 'endDate': endDate, 'fundId': fundId, 'username': username,
                  'code': code, 'bsFlag': bsFlag, 'matchType': matchType, 'orderNo': orderNo}
        rep = self.__request('getUserOptionKnock', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getNotice(self, code=[], beginDate=0, endDate=0, fields="*", keywords=""):
        """
        getNotice: 获取股票公告
        :param code: 证券代码或证券代码列表
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :param keywords: 关键词，多个关键词用空格分割
        :return: 
        """
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'beginDate': beginDate, 'endDate': endDate, 'code': code, 'fields': fields, 'keywords': keywords}
        rep = self.__request('getNotice', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getOptionBaseInfo(self, code=[], beginDate=0, endDate=0, fields="*"):
        """
        getOptionBaseInfo: 获取期权基础信息
        :param code: 证券代码或证券代码列表
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :return: 
        """
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'beginDate': beginDate, 'endDate': endDate, 'code': code, 'fields': fields}
        rep = self.__request('getOptionBaseInfo', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def callTs(self, script):
        """
        调用天软TSL脚本
        :param script: 脚本字符串，示例：return getbk("A股");
        :return: 函数返回值
        """
        script = script.strip()
        req = {'func': '', 'args': '', 'script': script}
        data = json.dumps(req)
        rep = self.__request('callTs', data=data)
        result = rep['result']
        return serialize.loads(result)

    def callTsFunc(self, func, args=None):
        """
        调用天软函数
        :param func: 函数名，示例：getbk
        :param args: 函数参数，示例：u'A股'
        :return: 函数返回值
        """
        args = serialize.dumps(args)
        req = {'func': func, 'args': args, 'script': ''}
        data = json.dumps(req)
        rep = self.__request('callTs', data=data)
        result = rep['result']
        return serialize.loads(result)

    def map(self, func=None, args=None, context=None):
        """
        :param func: Map函数
        :param args: Map参数
        :param context: 上下文参数
        :return: CoralParallelJob对象
        """
        from CoralParallelJob import CoralParallelJob
        url = "ws://%s:%s/parallel?token=%s" % (self._host, self._port, self._token)
        job = CoralParallelJob(url)
        return job.map(func, args, context)

    def __request(self, path, params=None, data=None, login=False):
        """
        """
        if params is None:
            params = {}
        if self._token:
            params['token'] = self._token
        for k, v in params.iteritems():
            if isinstance(v, unicode):
                params[k] = v.encode('UTF-8')
        url = 'http://%s:%s/%s?%s' % (self._host, self._port, path, urllib.urlencode(params))
        headers = {'User-Agent': 'PyCoralDB/1.1'}
        if data:
            headers['Content-Type'] = 'application/json'
        if self.compress:
            headers['Accept-Encoding'] = 'gzip'
        # Try to send the request a maximum of three times.
        for i in xrange(0, 3):
            try:
                req = urllib2.Request(url, data=data, headers=headers)
                f = urllib2.urlopen(req, timeout=10 if login else self.timeout)
                html = f.read()
                encoding = f.info().get('Content-Encoding')
                if encoding == 'gzip':
                    buf = StringIO.StringIO(html)
                    zf = gzip.GzipFile(fileobj=buf)
                    html = zf.read()
                    zf.close()
                rep = json.loads(html)
                if rep['error']:
                    err = '%s failed: %s' % (path, rep['error'])
                    raise Exception(err.encode('UTF-8'))
                return rep
            except urllib2.URLError, e:
                if not login and e.reason == 'Unauthorized':
                    self.login()
                    if self._token:
                        params['token'] = self._token
                    url = 'http://%s:%s/%s?%s' % (self._host, self._port, path, urllib.urlencode(params))
                    login = True
                    continue
                elif i < 2 and e.reason in ['Too Many Requests', 'Bad Gateway']:
                    time.sleep(10)
                    continue
                elif i < 2 and e.reason not in ['Forbidden', 'Bad Request']:
                    time.sleep(5)
                    continue
                else:
                    raise e
            except socket.timeout, e:
                if i >= 2:
                    raise e
            except socket.error, e:
                time.sleep(5)
                if i >= 2:
                    raise e
            except httplib.UnknownProtocol, e:
                time.sleep(5)
                if i >= 2:
                    raise e
        return None

if __name__ == '__main__':
    client = CoralDBClient('coraldb://127.0.0.1:5166')
    client.timeout = 5
    client.login("test", "123456")
    print client.getTradingDays()
