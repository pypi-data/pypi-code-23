#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import requests
import argparse

import qiniu

from ava.utils import utils
from ava.utils import uploader
from ava.log.logger import logger


class ImageUploader(object):
    """图片上传工具类
    负责：
        将本地图片上传至 kodo
        设置资源生命周期
        生成访问链接
    """

    def __init__(self, ak=None, sk=None, bucket=None):
        if ak and sk:
            self.ak, self.sk = ak, sk
        else:
            self.ak = utils.fetch_config_from_userinfo("key")
            self.sk = utils.fetch_config_from_userinfo("secret")
        if self.ak == None or self.sk == None:
            raise Exception("cannot init image uploader, no ak or sk")
        self.auth = qiniu.auth.Auth(self.ak, self.sk)
        if bucket:
            self.bucket = bucket
        else:
            self.bucket = utils.fetch_config_from_userinfo("bucket")
        self.bucket_domain = self._get_bucket_domain()
        self.kodo_key_prefix = "ava/default/tmp_imgs"
        self.uploader = uploader.Uploader(self.ak, self.sk, bucket=self.bucket)
        self.bucket_manager = qiniu.BucketManager(self.auth)

    def upload(self, filepath, delete_after_days=1):
        """上传本地文件至 kodo 并返回访问链接

        Args:
            filepath            : 本地文件路径
            delete_after_days   : 文件生存时间

        Returns:
            url    : 文件访问 URL

        Raises:
            exception   : 异常信息
        """
        if not os.path.exists(filepath):
            raise Exception("filepath does not exist, %s" % (filepath))
        file_name = os.path.basename(filepath)
        cur_ts = int(time.time())
        kodo_key = "%s/%s-%d" % (self.kodo_key_prefix, file_name, cur_ts)

        # 长传文件
        self.uploader.upload_file(filepath, kodo_key, bucket=self.bucket)
        # 设置过期删除天数
        ret, info = self.bucket_manager.delete_after_days(
            self.bucket, kodo_key, delete_after_days)
        if ret != {}:
            raise Exception("set delete after days failed, info: %s" % (info))
        # 返回访问 URL
        kodo_url = "http://%s/%s" % (self.bucket_domain, kodo_key)
        logger.debug("filepath: %s => %s", filepath, kodo_url)

        return kodo_url

    def _get_bucket_domain(self):
        """根据 bucket 名称获取空间域名

        Returns:
            domain_name : bucket domain

        Raises:
            Exception   : 发送错误时的异常
        """
        try:
            headers = {
                "User-Agent": "QiniuPython AVA",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            params = {
                "tbl": self.bucket,
            }

            resp = requests.get(url="http://api.qiniu.com/v6/domain/list",
                                auth=qiniu.auth.RequestsAuth(self.auth),
                                timeout=2000, headers=headers, params=params)

            if resp.status_code != requests.codes.ok:
                logger.error(
                    "resp.status should be 200,but got %s", resp.status_code)
                raise Exception("response status error")

            json_data = json.loads(resp.text)
            if isinstance(json_data, (list, tuple)) and len(json_data) > 0:
                # 默认返回第一个 domain
                return json_data[0]
            else:
                logger.error("resp.text:%s error", resp.text)
                raise Exception("response text error")
        except Exception as e:
            logger.error(e)
            raise e


def main():
    parser = argparse.ArgumentParser()
    auth_group = parser.add_argument_group("auth")
    auth_group.add_argument("--ak", help="qiniu access key", default=None)
    auth_group.add_argument("--sk", help="qiniu secret key", default=None)
    parser.add_argument(
        "--bucket", help="custom user qiniu bucket", default=None)
    parser.add_argument(
        "--days", help="delete resource after days", default="1")
    parser.add_argument("filepath", help="local file path")

    args = parser.parse_args()

    img_uploader = ImageUploader(ak=args.ak, sk=args.sk, bucket=args.bucket)
    url = img_uploader.upload(
        args.filepath, delete_after_days=args.days)
    print url


if __name__ == "__main__":
    main()
