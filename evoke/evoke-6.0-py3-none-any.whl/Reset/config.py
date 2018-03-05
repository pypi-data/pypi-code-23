# -*- coding: utf-8 -*-
"""
config file for evoke.Reset  (used by evoke.User)
"""

from evoke.data.schema import *


class Reset(Schema):
    "password reset request"
    user = INT, 0
    expires = DATE
    key = TAG
    stage = TAG, ''
