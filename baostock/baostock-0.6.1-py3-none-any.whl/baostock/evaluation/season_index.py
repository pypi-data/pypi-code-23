# -*- coding:utf-8 -*-
"""
估值指标，季频
@author: baostock.com
@group : baostock.com
@contact: baostock@163.com
@copyright: baostock System & alpha.All Rights Reserved.
"""
import time
import zlib
import baostock.data.resultset as rs
import baostock.common.contants as cons
import baostock.util.stringutil as strUtil
import baostock.common.context as conx
import baostock.util.socketutil as sock
import baostock.data.messageheader as msgheader


def query_dividend_data(code=None, year=None, yearType="report"):
    """估值指标（季频）,股息分红
    @param code: 证券代码，不可为空
    @param year: 年份，为空时默认当前年份
    @param yearType: 年份类别，默认为"report":预案公告年份，可选项"operate":除权除息年份
    """

    data = rs.ResultData()

    if code is None or code == "":
        print("股票代码不能为空，请检查。")
        data.error_msg = "股票代码不能为空，请检查。"
        data.error_code = cons.BSERR_PARAM_ERR
        return data
    if len(code) != 9:
        print("股票代码格式错误，请检查。")
        data.error_msg = "股票代码格式错误，请检查。"
        data.error_code = cons.BSERR_PARAM_ERR
        return data

    if year is None or year == "":
        year = time.strftime("%Y", time.localtime())
    if yearType is None or yearType == "":
        print("年份类别输入有误，请修改。")
        data.error_msg = "年份类别输入有误，请修改。"
        data.error_code = cons.BSERR_PARAM_ERR
        return data
    year = str(year)
    if not year.isdigit():
        print("年份输入有误，请修改。")
        data.error_msg = "年份输入有误，请修改。"
        data.error_code = cons.BSERR_PARAM_ERR
        return data

    user_id = ""
    try:
        user_id = getattr(conx, "user_id")
    except Exception:
        print("you don't login.")
        data.error_code = cons.BSERR_NO_LOGIN
        data.error_msg = "you don't login."
        return data

    param = "%s,%s,%s,%s,%s,%s,%s" % (
        "query_dividend_data", user_id, "1",
        cons.BAOSTOCK_PER_PAGE_COUNT, code, year, yearType)

    msg_body = strUtil.organize_msg_body(param)
    msg_header = msgheader.to_message_header(
        cons.MESSAGE_TYPE_QUERYDIVIDENDDATA_REQUEST, len(msg_body))

    data.msg_type = cons.MESSAGE_TYPE_QUERYDIVIDENDDATA_REQUEST
    data.msg_body = msg_body

    head_body = msg_header + msg_body
    crc32str = zlib.crc32(bytes(head_body, encoding='utf-8'))
    receive_data = sock.send_msg(head_body + cons.MESSAGE_SPLIT + str(crc32str))

    if receive_data is None or receive_data.strip() == "":
        data.error_code = cons.BSERR_RECVSOCK_FAIL
        data.error_msg = "网络接收错误。"
        return data

    msg_header = receive_data[0:cons.MESSAGE_HEADER_LENGTH]
    msg_body = receive_data[cons.MESSAGE_HEADER_LENGTH:-1]
    header_arr = msg_header.split(cons.MESSAGE_SPLIT)
    body_arr = msg_body.split(cons.MESSAGE_SPLIT)
    data.msg_body_length = header_arr[2]
    data.error_code = body_arr[0]
    data.error_msg = body_arr[1]

    if cons.BSERR_SUCCESS == data.error_code:
        data.method = body_arr[2]
        data.user_id = body_arr[3]
        data.cur_page_num = body_arr[4]
        data.per_page_count = body_arr[5]
        data.data = body_arr[6]
        data.code = body_arr[7]
        data.year = body_arr[8]
        data.yearType = body_arr[9]
        data.fields = body_arr[10]

    return data
