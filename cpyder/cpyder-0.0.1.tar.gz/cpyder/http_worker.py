# coding=utf-8
# author=spenly
# mail=i@spenly.com

import requests
import time
import urllib
from .utils import print_msg


def url_encode(words):
    """
    UrlEncode words
    :param words: words need to encode
    :return: string words after encode
    """
    return urllib.urlencode({"value": words})[6:]


def get_charset(headers):
    """
    get response encoding code by response header
    :param headers: response http header object
    :return: string encoding name
    """
    charset = "utf8"
    if "Content-Type" in headers:
        scs = str(headers["Content-Type"]).split(";")
        for s in scs:
            s = s.strip().lower().replace("-", '')
            if s.startswith("charset="):
                charset = s[8:]
                break
    return charset


def to_str(text, encoding=None):
    """
    trans any string or unicode object to string with UTF8
    :param text:
    :param encoding: old encoding if you know
    :return: string with utf8
    """
    if encoding:
        return text.decode(encoding)
    if not isinstance(text, str):
        try:
            text = text.decode("utf8")
        except UnicodeDecodeError:
            text = text.decode("gb2312")
    return text


class HttpWorker:
    """
    one simple utility based on requests
    """
    def __init__(self, time_out=30, error_sleep=10):
        """
        init
        :param time_out: request timeout
        :param error_sleep: sleep timeout when request error
        """
        self.proxy = None
        self.session = requests.session()
        self.time_out = time_out
        self.error_sleep_time = error_sleep

    def set_proxy(self, host, port, user="", pswd=""):
        """
        set proxy
        :param host:  proxy host
        :param port:  proxy port
        :param user:  proxy user account
        :param pswd:  proxy password
        :return:
        """
        if len(user) == 0:
            self.proxy = {"http": "http://%s:%s" % (host, port)}
        else:
            self.proxy = {"https": "http://%s:%s@%s:%s" % (user, pswd, host, port)}

    def clean_proxy(self):
        """
        clean proxy setting
        :return:
        """
        self.proxy = None

    def get(self, url, try_times=0, **kwargs):
        """

        :param url: 链接地址
        :param try_times: 已经重试次数, 如果请求失败, 自动尝试三次
        :param headers: 自定义请求头
        :return: 请求的内容
        """
        try:
            url = url.strip()
            print_msg("request[GET]: " + url)
            r = self.session.get(url, timeout=self.time_out, proxies=self.proxy, **kwargs)
            re_text = r.content
            charset = get_charset(r.headers)
            re_text = to_str(re_text, charset)
            return re_text
        except Exception as e:
            time.sleep(self.error_sleep_time)
            print_msg(("Request[GET] exception :", str(e)))
            try_times += 1
            if try_times < 3:
                print_msg("retrying ...")
                return self.get(url, try_times, **kwargs)
            else:
                return ''

    def post(self, url, post, try_times=0, **kwargs):
        """
        构造post请求
        :param url: 链接地址
        :param post: post 数据, dict对象
        :param try_times: 已经重试次数, 如果请求失败, 自动尝试三次
        :param headers: 自定义请求头
        :return: 请求的内容
        """
        try:
            url = url.strip()
            print_msg("Request[POST]: " + url)
            r = self.session.post(url, data=post, timeout=self.time_out, proxies=self.proxy, **kwargs)
            re_text = r.content
            charset = get_charset(r.headers)
            re_text = to_str(re_text, charset)
            return re_text
        except Exception as e:
            time.sleep(self.error_sleep_time)
            print_msg(("Request[POST] exception :", str(e)))
            try_times += 1
            if try_times < 3:
                print_msg("Retrying ...")
                return self.post(url, post, try_times, **kwargs)
            else:
                return ''

    def download(self, url, post=None, try_times=0, **kwargs):
        """
        构造文件下载请求
        :param url: 请求链接
        :param post: GET 方式为 None, Post 为 POST 数据, 默认为 None (GET)
        :param try_times: 已经重试次数, 如果请求失败, 自动尝试三次
        :return: 二进制对象
        """
        try:
            print_msg("Download [ %s ]:" % (post and "POST" or "GET") + url)
            if post:
                res = self.session.post(url, data=post, **kwargs).content
            else:
                res = self.session.get(url, timeout=self.time_out, **kwargs).content
            return res
        except Exception as e:
            time.sleep(self.error_sleep_time)
            print_msg(("Download exception:", str(e)))
            try_times += 1
            if try_times < 3:
                print_msg("Retrying ...")
                return self.download(url, post, try_times)
            else:
                return None
