#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import io
import time
import re


def reload_sys():
    reload(sys)
    sys.setdefaultencoding('utf8')


def reload_stdout():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')


# dire = os.path.dirname(os.path.abspath(__file__))
strftime = time.strftime('%Y%m%d', time.localtime())


def writelocaltxtfile(dire, local_filename, content):
    fi = os.path.join(dire, local_filename + '.txt')
    with open(fi, 'w', encoding='utf8') as f:
        f.write(content)


def writelocalbfile(dire, local_filename, content):
    fi = os.path.join(dire, local_filename)
    with open(fi, 'wb') as f:
        f.write(content)


def joinfoldfilename(fold, filename):
    if not os.path.exists(fold):
        os.makedirs(fold)
    path = os.path.join(fold, filename)
    return path


def textParse(bigString):  # input is big string, #output is word list
    listOfTokens = re.split(r'\W*', bigString)
    return [tok.lower() for tok in listOfTokens if len(tok) > 2]
