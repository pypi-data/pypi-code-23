# -*- coding: utf-8 -*-

import os
import qiniu


class Uploader(object):
    """将文件上报至Kodo"""

    def __init__(self, ak, sk, bucket=None):
        self.ak = ak
        self.sk = sk
        if bucket != None:
            self.default_bucket = bucket
        self.auth = qiniu.Auth(ak, sk)

    def set_bucket(self, bucket):
        self.bucket = bucket

    def upload_file(self, filepath, key, bucket=None):
        """上报单个文件至Kodo bucket中
        Args：
                filepath: 文件路径
                key: bucket key
                bucket: bucket名称，不提供的话，使用default_bucket

        Returns:
                return None when it's ok, or raise exception

        Raises:
                Exception, 当上报文件时发生错误，则raise Exception"""
        if not os.path.isfile(filepath):
            raise Exception(
                "file is not a existing regular file, filename: %s" % (filepath))
        if bucket == None:
            bucket = self.default_bucket

        token = self.auth.upload_token(bucket, key, 60)
        ret, info = qiniu.put_file(token, key, filepath)
        if not info.ok():
            raise Exception("upload failed, err: %s" % (info.error))
        if not (ret['key'] == key and ret['hash'] == qiniu.etag(filepath)):
            raise Exception("key or hash is not corrent, ret: %s" % (ret))

        return None
