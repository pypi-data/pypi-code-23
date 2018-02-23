# -*- coding:utf-8 -*-

"""
获取股票分类数据接口 

"""

import pandas as pd
from miceshare.db import mysql_access
import datetime
from functools import lru_cache
from miceshare.util.vars import *
from miceshare.util import vars


def get_industry_classified():
    """
        获取行业分类数据
    Returns
    -------
    DataFrame
        code :股票代码
        name :股票名称
        c_name :行业名称
    """
    pass

def get_board_list(channel = 0):
    """
    获取板块列表
    :return:
        DataFrame
            code:概念
            name:概念名称
            type:类型
            channel:来源
    """
    boards = mysql_access.board_dao.select()
    data = pd.DataFrame(boards, columns=['code', 'name','type','channel'])
    data = data[data['channel'] == channel]
    return data


@lru_cache(None)
def get_board_name(board_code):
    board_list = get_board_list()
    board_list[board_list['code'] == board_code]['name'].tolist()

def get_concept_stocks(concept,channel,date=None):
    """
    获取概念板块下的股票列表
    :param name: 板块名称
    :param channel:渠道1是同花顺
    :param date:股票上市日期，暂时无用
    :return:
    """
    return mysql_access.board_stock_dao.query_stocks_by_board(concept,vars.Board_C,channel)


@lru_cache(None)
def get_concept_for_stock(stock,channel=0):
    """
        获取概念列表
    Return
    --------
    ['概念名称']
    """
    concept = get_concept_classified()
    board_code_list = concept[concept['stock_code'] == stock]
    board_list = get_board_list(channel)
    m = pd.merge(board_code_list, board_list,left_on='board',right_on='code')
    return m['name'].tolist()

@lru_cache(None)
def get_concept_classified():
    """
        获取概念分类数据
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
        c_name :概念名称
    """
    l = mysql_access.board_stock_dao.select()
    return pd.DataFrame(l, columns=['stock_code', 'board'])


def get_area_classified():
    """
        获取地域分类数据
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
        area :地域名称
    """
    pass


def get_gem_classified():
    """
        获取创业板股票
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
    """
    df = get_stock_basics()
    df = df.ix[df.code.str[0] == '3']
    df = df.sort_values('code').reset_index(drop=True)
    return df
    

def get_sme_classified():
    """
        获取中小板股票
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
    """
    df = get_stock_basics()
    df = df.ix[df.code.str[0:3] == '002']
    df = df.sort_values('code').reset_index(drop=True)
    return df 

def get_st_classified():
    """
        获取风险警示板股票
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
    """
    df = get_stock_basics
    df.reset_index(inplace=True)
    df = df.ix[df.name.str.contains('ST')]
    df = df.sort_values('code').reset_index(drop=True)
    return df 

@lru_cache(None)
def get_stock_basics(time=None):
    """
    查询股票列表
    :param time 截止上市日期
    :return:
    DataFrame
        code :股票代码
        name :股票名称
        start_date :日期
        exchange:市场 sz或sh
    """
    if time is None:
        time = datetime.datetime.now().date()
    l = mysql_access.stock_dao.select(time)
    return pd.DataFrame(l,columns=['code','name','start_date','exchange'])

def get_hs300s():
    """
    获取沪深300当前成份股及所占权重
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
        date :日期
        weight:权重
    """
    pass


def get_sz50s():
    """
    获取上证50成份股
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
    """
    pass


def get_zz500s():
    """
    获取中证500成份股
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
    """
    pass


def get_terminated():
    """
    获取终止上市股票列表
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
        oDate:上市日期
        tDate:终止上市日期 
    """
    pass


def get_suspended():
    """
    获取暂停上市股票列表
    Return
    --------
    DataFrame
        code :股票代码
        name :股票名称
        oDate:上市日期
        tDate:终止上市日期 
    """
    pass


def insert_board(code, name, type=Board_C, channel=0):
    """
    插入概念板块数据
    :param code:
    :param name:
    :return:
    """
    mysql_access.board_dao.insert(code, name, type,channel)

def insert_board_stock(stock_code,board_code):
    """
    插入股票和板块的关系
    :param stock_code:
    :param board_code:
    :return:
    """
    mysql_access.board_stock_dao.insert(stock_code, board_code)