# -*- coding:utf-8 -*-
"""
K线数据
"""

def get_k_stock_d():
    pass

def get_k_stock_m():
    pass


def get_k_index_d():
    pass

def get_k_index_m():
    pass

def get_k_board_d(code,start,end,count=30,autype='qfq',ktype='D'):
    """
    获取k线数据-板块
    ---------
    Parameters:
      code:string
                  板块代码 e.g. 885756
      start:string
                  和count选其一，开始日期 format：YYYY-MM-DD 为空时取上市首日
      end:string
                  结束日期 format：YYYY-MM-DD 为空时取最近一个交易日
      count:int
                  和star选其一，如果只指定结束日期，则使用个数
      autype:string
                  复权类型，qfq-前复权 hfq-后复权 None-不复权，默认为qfq
      ktype：string
                  数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
    return
    -------
      DataFrame
          date 交易日期 (index)
          open 开盘价
          high  最高价
          close 收盘价
          low 最低价
          volume 成交量
          amount 成交额
          code 代码
    """




def get_k_board_d():
    pass