#!/usr/bin/env python
# -*- coding:utf-8 -*-


__author__ = 'bee'

from .models import UserExamRecord


# django前台显示本地时间
def filter_local_datetime(_datetime):
    return _datetime


# 学生报名后续操作
def after_user_exam_add(record):
    return True, ""


# 学生报名前操作
def before_user_exam(user_id):
    return True, ""


# 通过考级后操作
def after_user_passed(record):
    return True, ""


def get_user_icon(user_id):
    if not user_id:
        return None
    record_list = UserExamRecord.objects.filter(user__id=user_id, is_passed=True).order_by("-created_at")
    if record_list.count() >= 1:
        record = record_list.first()
        try:
            icon = record.grade.icon
            return icon.url
        except:
            return None
    else:
        return None
