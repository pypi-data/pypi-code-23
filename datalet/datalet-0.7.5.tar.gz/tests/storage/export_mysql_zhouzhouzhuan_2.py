#!/usr/bin/env python
# -*- coding: utf-8  -*-

"""
execute the unittest file in project root directory.
"""
import sys
sys.path.insert(0, r"../datalet")

import unittest

import pandas as pd

from datalet.data import *
from datalet.storage import *
from datalet.storage.dbtable_storage import *
import datalet.storage.facade as sfd
from sqlalchemy import create_engine

mysql_db_url = create_mysql_dburl("localhost", "abc", "abc", "123456", port = 8866)
engine = create_engine(mysql_db_url)

#sql_yueyuefa = "" \
#" select cp.id, cp.uid, cp.corp, cp.status, cp.type, cp.fund, cp.refund, cp.paidfund, cp.service, cp.paidservice, cp.penalty, cp.paidpenalty, cp.paytime, cp.expiredate, cp.period, cp.applyuid from credit_payment cp;"
# sql_yueyuefa = "" \
# " select *, (t1.not_paidfund + t1.not_paidservice + t1.not_paidpenalty) as not_sum from (" \
# " select cp.id, cp.uid, cp.corp, cp.status, cp.type, " \
# " 	cp.fund, cp.refund, cp.paidfund, cp.service, " \
# "     cp.paidservice, cp.penalty, " \
# "     cp.paidpenalty, cp.paytime, cp.expiredate, " \
# "     cp.period, cp.applyuid ," \
# "     cp.clearofftime," \
# "     (cp.fund - cp.paidfund - cp.refund) as not_paidfund," \
# "     (cp.service - cp.paidservice) as not_paidservice," \
# "     (cp.penalty - cp.paidpenalty) as not_paidpenalty," \
# "     case cp.status" \
# " 		when 1 then 0" \
# "         when 2 then 0" \
# "         when 3 then floor((UNIX_TIMESTAMP(cp.clearofftime) - UNIX_TIMESTAMP(cp.expiredate)) / (60*60*24))" \
# "         when 4 then -1" \
# "         else null" \
# " 	end as expired_days" \
# " from credit_payment cp) t1 " \
#" where t1.status = 4";

sql_yueyuefa = "" \
" select full_table.*,  " \
" 		(full_table.not_paidfund + full_table.not_paidservice + full_table.not_paidpenalty) as not_sum,  " \
" 		ai.acct_name, ai.filter_company_name, ai.trade1_name, ai.trade2_name, year(full_table.paytime) as pay_year  " \
" from  " \
 " (  " \
" 	select t1.* from " \
" 		(select cp.id, cp.uid, cp.corp, cp.status, cp.type,   " \
" 			cp.fund, cp.refund, cp.paidfund, cp.service,   " \
" 			 cp.paidservice, cp.penalty,   " \
" 			 cp.paidpenalty, cp.paytime, cp.expiredate,   " \
" 			 cp.period, cp.applyuid ,  " \
" 			 cp.clearofftime,  " \
" 			 (cp.fund - cp.paidfund - cp.refund) as not_paidfund,  " \
" 			 (cp.service - cp.paidservice) as not_paidservice,  " \
" 			 (cp.penalty - cp.paidpenalty) as not_paidpenalty,  " \
" 			 case cp.status  " \
" 				when 1 then 0  " \
" 				 when 2 then 0  " \
" 				 when 3 then floor((UNIX_TIMESTAMP(cp.clearofftime) - UNIX_TIMESTAMP(cp.expiredate)) / (60*60*24))  " \
" 				 when 4 then -1  " \
" 				 else null  " \
" 			end as expired_days  " \
" 		from yueyuefa.credit_payment cp) t1   " \
 " ) " \
" full_table  " \
" left join yueyuefa.ods_fc_acct_info ai on full_table.uid = ai.acct_id "

result = engine.execute(text(sql_yueyuefa), {})
ret_all = result.fetchall()
#first = ret_all[:5]
#print(first)

dt_zhouzhouzhuan = DataTable("table_zhouzhouzhuan",
	DataColumn(name = "id", caption = "信用加款流水号"),
	DataColumn(name = "uid", caption = "账户ID"),
	DataColumn(name = "acct_name", caption = "账户名称"),
	DataColumn(name = "filter_company_name", caption = "客户公司名称"),
	DataColumn(name = "trade1_name", caption = "一级行业"),
	DataColumn(name = "trade2_name", caption = "二级行业"),
	DataColumn(name = "corp", caption = "所属分公司"),
	DataColumn(name = "status", caption = "当前支付状态"),
	DataColumn(name = "type", caption = "信用支付属性"),
	DataColumn(name = "fund", caption = "信用加款金额"),
	DataColumn(name = "refund", caption = "信用退款金额"),
	DataColumn(name = "paidfund", caption = "已还信用款额"),
	DataColumn(name = "not_paidfund", caption = "未还信用款额"),
	DataColumn(name = "service", caption = "手续费"),
	DataColumn(name = "paidservice", caption = "已还手续费"),
	DataColumn(name = "not_paidservice", caption = "未还手续费"),
	DataColumn(name = "penalty", caption = "违约金"),
	DataColumn(name = "paidpenalty", caption = "已还违约金"),
	DataColumn(name = "not_paidpenalty", caption = "未还违约金"),
	DataColumn(name = "not_sum", caption = "欠款总额"),
	DataColumn(name = "paytime", caption = "信用加款时间"),
	DataColumn(name = "expiredate", caption = "还款截止时间"),
	DataColumn(name = "period", caption = "授信账期"),
	DataColumn(name = "expired_days", caption = "逾期天数"),
	DataColumn(name = "applyuid", caption = "申请客服"),
	DataColumn(name = "pay_year", caption = "支付年份"))

for row in ret_all:
	dt_zhouzhouzhuan.append(dict(row))

print(len(dt_zhouzhouzhuan))

sfd.write_file(r"D:\zhouzhouzhuan_acct.xlsx", data = dt_zhouzhouzhuan, sheetIndex = 0, force = True, overwrite=True)

# es_yueyuefa = sfd.create_file(r"D:\yueyuefa.xlsx", sheetIndex = 0, force = True)
# if es_yueyuefa.exists_file():
	# es_yueyuefa.remove()
# es_yueyuefa.write(data = dt_yueyuefa)
