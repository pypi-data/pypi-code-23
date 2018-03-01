# -*- coding: utf-8 -*-
"""
网络请求模块
"""

import os
import json
import types
import re
import qiniu.auth
from qiniu.http import ResponseInfo
import requests

from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPClient, AsyncHTTPClient, HTTPRequest, HTTPError
from tornado.httputil import HTTPHeaders
from urlparse import urlparse

from ava.log.logger import logger

USER_AGENT = 'QiniuPython AVA'

_headers = {'User-Agent': USER_AGENT,
            'Content-Type': "application/x-www-form-urlencoded"}

pattern = re.compile("/(.*?)/(.*)")


class Fetcher(object):
    """ 网络请求的封装，支持同步和异步两种方式，且支持使用七牛源站下载和失败重试。 """

    DEFAULT_CONNECT_TIMEOUT = 20
    DEFAULT_REQUEST_TIMEOUT = 600  # 默认下载超时10分钟，防止大文件下载超时
    HUGE_FILE_REQUEST_TIMEOUT = 72000 # 默认下载超大文件的超时时间，20个小时
    DEFAULT_MAX_RETRY = 5
    DEFAULT_MAX_BUFFER_SIZE = 1073741824  # 默认最大下载文件1G
    DOWNLOAD_POOL_SIZE = 75

    def __init__(
            self,
            _async=False,
            access_key=None,
            secret_key=None,
            req_timeout=None,
            download_pool=None,
            max_buffer_size=None):
        """ 初始化 Fetcher

        Args:
            _async: 使用同步请求还是下异步请求，默认使用同步请求。
            access_key: 七牛账号的 access_key，默认为 None。
            secret_key: 七牛账号的 secret_key，默认为 None。
            req_timeout: 超时时间，默认为 None。
            download_pool: 请求最大并发数，默认为 None。
            max_buffer_size: 最大下载大小，默认为 None。
        """
        self.async = _async
        self.ioloop_instance = IOLoop.instance() if _async else None
        self.access_key = access_key
        self.secret_key = secret_key
        self.req_timeout = req_timeout

        self._is_fetch_huge_file = False
        self._file_content_length = 0
        self._file_download_length = 0

        if self.access_key is None or self.secret_key is None:
            self.auth = None
        else:
            try:
                self.auth = qiniu.auth.Auth(self.access_key, self.secret_key)
            except Exception as err:
                logger.error(("qiniu.Auth(%s,%s) with Error Msg:%s"),
                             self.access_key, self.secret_key, err)

        max_buffer_size = max_buffer_size or Fetcher.DEFAULT_MAX_BUFFER_SIZE
        download_pool = download_pool or Fetcher.DOWNLOAD_POOL_SIZE
        self.http_client = HTTPClient(max_buffer_size=max_buffer_size) \
            if not _async else AsyncHTTPClient(
            max_buffer_size=max_buffer_size,
            max_clients=download_pool)

    def __del__(self):
        if self.http_client is not None:
            self.http_client.close()
        if self.ioloop_instance is not None:
            self.ioloop_instance.stop()

    def start_tornado_ioloop(self):
        self.ioloop_instance.start()

    def stop_tornado_ioloop(self):
        self.ioloop_instance.stop()

    def parse_qiniu_url(self, path):
        '''
        convert the qiniu://zone/bucket/key to http://domain/key
        :param path:path 是/bucket/key
        :return: normal uri
        '''
        match = pattern.match(path)
        if not match:
            logger.error("pattern.match(%s) failed:", path)
            raise Exception("qiniu url not correct")

        bucket = match.group(1)

        key = match.group(2)

        host = self._get_qiniu_domain(bucket=bucket)
        uri = "http://%s/%s" % (host, key)

        return uri, host

    def _get_qiniu_domain(self, bucket, num_tries=3):
        '''
        get the qiniu domain with the params of bucket and ak,sk
        :param bucket: bucket name
        :param num_tries: 尝试多少次
        :return: 返回domain的名字
        '''
        try:
            params = {"tbl": bucket}
            resp = requests.get(url="http://api.qiniu.com/v6/domain/list",
                                auth=qiniu.auth.RequestsAuth(self.auth),
                                timeout=2000, headers=_headers, params=params)

            if resp.status_code != requests.codes.ok:
                if num_tries >= 0:
                    return self._get_qiniu_domain(num_tries=num_tries - 1, bucket=bucket)
                logger.error(
                    "resp.status should be 200,but got %s", resp.status_code)
                raise Exception("response status error")

            json_data = json.loads(resp.text)
            if json_data:
                return json_data[0]
            else:
                logger.error("resp.text:%s error", resp.text)
                raise Exception("response text error")
        except Exception as e:

            if num_tries >= 0:
                return self._get_qiniu_domain(num_tries=num_tries - 1, bucket=bucket)
            logger.error(e)
            raise e

    def _process_kodo_request(self, url, headers):
        url_res = urlparse(url)
        host = url_res.hostname
        # 如果 提供ak,sk，则说明可能是需要授权的
        if url_res.scheme == "qiniu":
            temp_uri, host = self.parse_qiniu_url(url_res.path)
            if temp_uri:
                url = temp_uri
            else:
                raise Exception("qiniu protocol url")

        if self.auth:
            url_splited = url.split("?")
            url_base = url_splited[0]

            url = self.auth.private_download_url(
                url_base, expires=36000)
            if len(url_splited) > 1:
                url = '{0}&{1}'.format(url, url_splited[1])

        url = url.replace(host, "iovip.qbox.me")

        if not headers:
            headers = HTTPHeaders()
        elif isinstance(headers, types.DictType):
            headers = HTTPHeaders(headers)
        headers.add("Host", host)
        return url, headers

    def fetch(
            self,
            url,
            method="GET",
            headers=None,
            data=None,
            from_kodo=False,
            retry=0,
            max_retry=-1,
            callback=None,
            cb_args=None,
            cb_kargs=None):
        """ 发起网络请求
        Args:
            url: 请求地址。
            method: 请求方法，默认为 GET 方法。
            headers: 请求的 Headers，默认为 None。
            data: 请求的 body，默认为 None。注意 method 为 GET 时，不支持 data 参数。
            from_kodo: 是否从七牛源站下载，默认为 False
            retry: 当前重试的次数，默认为 0。max_retry 为负时无效。
            max_retry: 允许的最多重试次数，默认为 -1。为负时表示不重试，为 0 时表示使用默认最大重试次数。
            callback: 请求结束后的回调，默认为 None。只在异步 Fetcher 实例下有效。
            cb_args: 传入 callback 的参数。
            cb_kargs: 传入 callback 的参数。

        Returns:
            (res, err): 请求的响应对象(tornado.httpclient.HTTPResponse)
            和请求错误对象(tornado.httpclient.HTTPError)。
            只有同步 Fetcher 实例有返回。
        """
        max_retry = max_retry if max_retry != 0 else self.DEFAULT_MAX_RETRY

        # fetch from origin host if resource is from kodo
        if from_kodo and retry == 0:
            url, headers= self._process_kodo_request(url, headers)
        if isinstance(data, types.DictType):
            data = json.dumps(data, encoding="UTF-8")

        connect_timeout = Fetcher.DEFAULT_CONNECT_TIMEOUT * (1 + 0.4 * retry)
        request_timeout = self.req_timeout or (
            Fetcher.DEFAULT_REQUEST_TIMEOUT * (1 + 0.4 * retry))
        request = HTTPRequest(
            url,
            method,
            headers=headers,
            body=data,
            connect_timeout=connect_timeout,
            request_timeout=request_timeout)

        if not self.async:
            res = None
            try:
                res = self.http_client.fetch(request)
            except (HTTPError, Exception) as err:
                if max_retry > 0 and retry < max_retry:
                    logger.warning(
                        ("http request from '%s' failed after retried for " +
                         "%d times, max retry: %d. Error message: %s"),
                        url, retry + 1, max_retry, err)
                    return self.fetch(
                        url,
                        method,
                        headers,
                        data,
                        from_kodo,
                        retry + 1,
                        max_retry,
                        callback,
                        cb_args,
                        cb_kargs)
                elif max_retry > 0:
                    logger.error(
                        ("http request from '%s' failed after retry: %d. " +
                         "Error message: %s"), url, max_retry, err)
                else:
                    logger.error(
                        "http request from '%s' failed! Error message: %s",
                        url, err)
                return (res, err)
            else:
                return (res, None)
        else:
            def handle_response(response):
                if response.error:
                    if max_retry > 0 and retry < max_retry:
                        logger.warning(
                            ("http request from '%s' failed after retried " +
                             "for %d times, max retry: %d. Error message: %s"),
                            url, retry + 1, max_retry, response.error)
                        return self.fetch(
                            url,
                            method,
                            headers,
                            data,
                            from_kodo,
                            retry + 1,
                            max_retry,
                            callback,
                            cb_args,
                            cb_kargs)
                    elif max_retry > 0:
                        logger.error(
                            ("http request from '%s' failed after " +
                             "retry: %d. Error message: %s"),
                            url, max_retry, response.error)
                    else:
                        logger.error(
                            "http request from '%s' failed! Error message: %s",
                            url, err)
                callback(response, response.error, cb_args, cb_kargs)

            self.http_client.fetch(request, handle_response)

    def fetch_huge_file(self, url, filepath=None, headers=None, chunk_size=1024, progress_callback=None):
        """
        streamly fetch huge file to local disk
        """
        if self._is_fetch_huge_file:
            raise Exception(
                "current fetcher is downloading a file, "
                + "please initial anthor fetcher instance, "
                + "or wait until current fetch task done")

        self._is_fetch_huge_file = True

        if url.startswith("qiniu://"):
            url, headers = self._process_kodo_request(url, headers)

        parse_result = urlparse(url)
        filepath = filepath or os.path.split(parse_result.path)[1]
        path_folder, _basename = os.path.split(filepath)
        if path_folder and not os.path.exists(path_folder):
            os.mkdir(path_folder)

        length_header_reg = re.compile(r'content-length:\s*(\d+)', re.IGNORECASE)
        local_file = open(filepath, "a+")
        def _header_callback(line):
            result = length_header_reg.search(line)
            if result:
                self._file_content_length = int(result.group(1))

        def _streaming_callback(chunk_bytes):
            local_file.write(chunk_bytes)
            if progress_callback:
                self._file_download_length += len(chunk_bytes)
                progress = float(self._file_download_length) / self._file_content_length
                if progress == 1.0:
                    _complete_callback()
                progress_callback(progress)

        def _complete_callback():
            local_file.close()
            self._is_fetch_huge_file = False
            self._file_content_length = 0
            self._file_download_length = 0

        req = HTTPRequest(
            url,
            "GET",
            headers=headers,
            header_callback=_header_callback,
            streaming_callback=_streaming_callback,
            request_timeout=Fetcher.HUGE_FILE_REQUEST_TIMEOUT)
        self.http_client.fetch(req)

class QMacAuthFetcher(object):
    """
    七牛带鉴权服务请求的封装
    """
    DEFAULT_MAX_RETRY = 5

    def __init__(self, access_key, secret_key):
        """
        Args:
            access_key: 用户的access_key
            secret_key: 用户的secret_key
        """
        self.auth = qiniu.auth.QiniuMacRequestsAuth(
            qiniu.auth.QiniuMacAuth(access_key, secret_key))

    def fetch(self, url, method="GET", data=None, headers=None, retry=0, max_retry=-1):
        """
        Args:
            url: 请求地址
            method: 请求方法
            data: 请求数据
            headers: 请求头部
            retry: 当前重试次数，默认为0
            max_retry: 最大重试次数，默认为-1表示不重试。为0时表示使用此Fetcher的默认重试次数。

        Returns:
            (res, err) 请求的响应对象(requests.Response)
            和请求错误对象(tornado.httpclient.HTTPError)。
        """
        max_retry = max_retry if max_retry != 0 else self.DEFAULT_MAX_RETRY

        res = None
        method = method.lower()
        try:
            if method == "get":
                res = requests.get(url, auth=self.auth)
            elif method == "post":
                res = requests.post(
                    url, json=data, auth=self.auth, headers=headers)
            elif method == "put":
                res = requests.put(
                    url, json=data, auth=self.auth, headers=headers)
            else:
                raise Exception("method `{0}` not support now".format(method))
            info = ResponseInfo(res)
            assert info.ok(), (info.status_code, info.error)
            return (res, None)
        except Exception as err:
            if retry < max_retry:
                logger.warning(
                    ("http request from '%s' failed after retried for " +
                     "%d times, max retry: %d. Error message: %s"),
                    url, retry + 1, max_retry, err)
                return self.fetch(url, method, data, headers, retry + 1, max_retry)
            elif max_retry > 0:
                logger.error(
                    ("http request from '%s' failed after retry: %d. " +
                        "Error message: %s"), url, max_retry, err)
            else:
                logger.error(
                    "http request from '%s' failed! Error message: %s",
                    url, err)
            return (res, err)
