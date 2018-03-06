#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
from utils import get_now
from .models import Poster, PreUserContract

__author__ = 'zhangyue'


# 获取显示的海报<poster_id>列表
# 生成的海报路径为：/<CRM_POSTER_PHOTO_PATH>/<poster_id>/<user_id>_poster.jpg
def get_poster_show_list():
    posters = Poster.objects.filter(is_show=True)
    show_list = []
    for poster in posters:
        show_list.append(poster.id)
    return show_list


# 随机获取海报id
def get_random_poster_id():
    posters = get_poster_show_list()
    if len(posters) == 0:
        return None
    poster_id = random.choice(posters)
    return poster_id


# django前台显示本地时间
def filter_local_datetime(_datetime):
    return _datetime


# 费用审核后续操作
def after_check_callback(preuser_contract_id):
    try:
        preuser_contract = PreUserContract.objects.get(id=preuser_contract_id)
        preuser_contract.after_checked_at = get_now()
        preuser_contract.save()
        return True, None
    except Exception as e:
        return False, e.__str__()


# 获取合同的天数
# return month/week,<时长>
def get_peruser_contract_days(preuser_contract_id):
    try:
        peruser_contract = PreUserContract.objects.get(id=preuser_contract_id)
        contract = peruser_contract.contract
        return contract.period, contract.duration
    except:
        return None, None


# 获取合同的开始日期
# return month/week,<时长>
def get_peruser_contract_start_day(preuser_contract_id):
    try:
        peruser_contract = PreUserContract.objects.get(id=preuser_contract_id)
        return peruser_contract.study_at
    except:
        return None
