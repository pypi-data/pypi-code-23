#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from .utils import get_login_user, get_coin_type
from .models import CoinType, UserCoinRecord


# django前台显示本地时间
def filter_local_datetime(_datetime):
    return _datetime


def get_user(request):
    return get_login_user(request)


# 操作消息记录，返回结果
def add_coin_record(to_user, reason=None, identity=None, coin=None, created_by=None):
    try:
        record = UserCoinRecord()
        record.user = to_user
        coin_type = get_coin_type(identity)
        record.coin_type = coin_type
        if coin:
            record.coin = coin
        elif coin_type:
            record.coin = coin_type.coin
        record.reason = reason
        record.created_by = created_by
        record.save()
        return record.coin
    except Exception as e:
        print('bee_django_coin->add_coin_record->error:' + e.__str__())
        return None
