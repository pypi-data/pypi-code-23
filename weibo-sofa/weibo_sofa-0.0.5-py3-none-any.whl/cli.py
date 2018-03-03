# -*- coding: utf-8 -*-


""" 
@author: W@I@S@E 
@contact: wisecsj@gmail.com 
@site: https://wisecsj.github.io 
@file: cli.py
@time: 2018/3/2 20:07
"""
import argparse
import pickle
import sys
import os

from .log import logger

try:
    import fcntl

    LINUX = True
except ImportError:
    logger.exception('此功能不支持Windows，抱歉～')
    LINUX = False
    sys.exit()


class CLI:
    def __init__(self):
        self.path = None
        self.p = argparse.ArgumentParser()
        self.p.add_argument('operation', help='add|delete')
        self.p.add_argument('-u', help='user id')
        self.p.add_argument('-p', help='record file path,when not specified,is cwd')

    def run(self):
        # parse
        p = self.p
        args = p.parse_args()
        opt = args.operation
        uid = args.u
        self.path = args.p or os.path.join(os.getcwd(),'record')
        # execute
        try:
            self.__getattribute__('_' + opt)(uid)
        except Exception as e:
            sys.exit('添加或删除uids出错')

    def unpickle_record(self):
        with open(self.path, 'rb') as f:
            record = pickle.load(f)
        return record

    def pickle_record(self, record):
        with open(self.path, 'wb') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            pickle.dump(record, f)

    def _add(self, uid):
        """
        add uid to pickle file 'record'
        """
        record = self.unpickle_record()
        uids = record.get('uids', [])
        uids.append(uid)
        record['uids'] = uids
        self.pickle_record(record)

    def _delete(self, uid):
        record = self.unpickle_record()
        uids = record.get('uids', [])
        try:
            uids.remove(uid)
        except:
            pass
        record['uids'] = uids
        self.pickle_record(record)


def main():
    c = CLI()
    c.run()
