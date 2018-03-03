# -*- coding: utf-8 -*-


""" 
@author: W@I@S@E 
@contact: wisecsj@gmail.com 
@site: https://wisecsj.github.io 
@file: config.py 
@time: 2018/2/19 20:20 
"""

import sys
import os

LOGFILE_PATH = os.path.join(os.path.dirname(sys.argv[0]), 'weibo.log')
RECORD_PATH = os.path.join(os.path.dirname(sys.argv[0]), 'record')

# logger Stream handler level
DEBUG = False

# comment content
CONTENT = '沙发'

# sleep after a loop
INTERVAL = (1, 1.5, 2)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# 需要抢其沙发的用户uid
# 测试号；鱼；PUBG；angrybb
UID = ['5860185885', '2914927101', '6037906900', '1903031221']
