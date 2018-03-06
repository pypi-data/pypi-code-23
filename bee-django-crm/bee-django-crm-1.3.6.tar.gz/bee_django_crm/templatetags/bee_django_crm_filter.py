#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from datetime import datetime
from django import template
from bee_django_crm.utils import change_tz, LOCAL_TIMEZONE, get_referral_user_name_with_preuser, get_track_list, \
    get_user_name
from bee_django_crm.models import APPLICATION_QUESTION_INPUT_TYPE_CHOICES
from bee_django_crm.exports import filter_local_datetime

register = template.Library()


# 获取转介人姓名
@register.filter
def get_referral_user_name(preuser):
    referral_user = preuser.referral_user
    if not referral_user:
        return None
    return get_user_name(referral_user)


# 获取联络次数
@register.filter
def get_preuser_track_list(preuser_id):
    return get_track_list(preuser_id)


# 获取自定义user的自定义name
@register.filter
def get_checked_user_name(user):
    return get_user_name(user)


# 本地化时间
@register.filter
def local_datetime(_datetime):
    return filter_local_datetime(_datetime)


# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)


# 返回option的html
@register.filter("get_html")
def get_html(application, id):
    if not application:
        return ""
    html = "<div>"
    question = application["question"]
    question_name = question.name
    html += "<div>" + id.__str__() + " . " + question_name + "</div>"
    options = application["options"]

    # 输入框
    if question.input_type == APPLICATION_QUESTION_INPUT_TYPE_CHOICES[0][0]:
        html += "<div><input type='text' name='input_" + id.__str__() + "' id=""></div>"
    # 单选圆钮
    elif question.input_type == APPLICATION_QUESTION_INPUT_TYPE_CHOICES[1][0]:
        for option in options:
            html += "<input type='radio' name='input_" + id.__str__() + "' value=" + option.name + "> " + option.name + " "
    # 单选下拉
    elif question.input_type == APPLICATION_QUESTION_INPUT_TYPE_CHOICES[2][0]:
        html += "<select name='input_" + id.__str__() + "'>"
        for option in options:
            html += "<option  value='" + option.name + "'>" + option.name + "</option>"
        html += "</select>"
    # 多选方钮
    elif question.input_type == APPLICATION_QUESTION_INPUT_TYPE_CHOICES[3][0]:
        for option in options:
            html += "<input type='checkbox' name='input_" + id.__str__() + "' value='" + option.name + "'> " + option.name + "<br>"
    html += "</div>"
    return html
