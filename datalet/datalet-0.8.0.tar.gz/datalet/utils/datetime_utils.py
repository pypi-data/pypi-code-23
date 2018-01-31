#!/usr/bin/env python
# -*- coding: utf-8  -*-

import datetime
from dateutil.relativedelta import *
import calendar

def get_week_date_range(date_val, start_weekday = 7):
	'''
	返回指定日期所在周的日期列表。

	Args:
		date_val: date type or date like string.
		start_weekday: 周的起始天。默认为7。
			1表示以周一作为周的起始日，
			2表示以周二作为周的起始日，
			3表示以周三作为周的起始日，
			4表示以周四作为周的起始日，
			5表示以周五作为周的起始日，
			6表示以周六作为周的起始日，
			7表示以周日作为周的起始日。
	'''
	if (start_weekday < 1) or (start_weekday > 7):
		raise Exception('start_weekday argument value out of range.')
	if isinstance(date_val, str):
		date_val = datetime.datetime.strptime(date_val, '%Y-%m-%d').date()
	if not isinstance(date_val, datetime.date):
		raise Exception('date_val is not a date')
	week_date_range = []
	cur_weekday = date_val.weekday()
	cur_weekday += 1

	start_timedelta = (start_weekday - cur_weekday) if cur_weekday >= start_weekday else ( start_weekday - cur_weekday - 7)
	end_timedelta = start_timedelta + 6

	for td in range(start_timedelta, end_timedelta + 1):
		week_date = date_val + datetime.timedelta(days = td)
		week_date_range.append(week_date)
	return week_date_range

def get_week_date_range_text(date_val, start_weekday = 7, date_format = "%m.%d", seprator = "-"):
	'''
	获取指定日期所在周的范围表示文本

	默认格式为 mm.dd-mm.dd
	'''
	d_range = get_week_date_range(date_val, start_weekday)
	return d_range[0].strftime(date_format) + seprator + d_range[-1].strftime(date_format)


def xdaterange(start, end):
	pass

def parse_date(str, format):
	pass

def format_date(d, format):
	pass
