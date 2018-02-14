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
        send GET request
        :param url: url
        :param try_times: tried times after failing
        :return: text
        """
        try:
            url = url.strip()
            print_msg("request[GET]: " + url)
            r = self.session.get(url, timeout=self.time_out, proxies=self.proxy, **kwargs)
            re_text = r.text
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

    def post(self, url, try_times=0, **kwargs):
        """
        send POST request
        :param url: url
        :param try_times: tried times after failing
        :return: text
        """
        try:
            url = url.strip()
            print_msg("Request[POST]: " + url)
            r = self.session.post(url, timeout=self.time_out, proxies=self.proxy, **kwargs)
            re_text = r.text
            return re_text
        except Exception as e:
            time.sleep(self.error_sleep_time)
            print_msg(("Request[POST] exception :", str(e)))
            try_times += 1
            if try_times < 3:
                print_msg("Retrying ...")
                return self.post(url, try_times, **kwargs)
            else:
                return ''

    def download(self, url, method="GET", try_times=0, **kwargs):
        """
        download file
        :param url: url
        :param method: GET or POST, default GET
        :param try_times: tried times after failing
        :return: content
        """
        try:
            post = method.upper() == "POST"
            print_msg("Download [ %s ]:" % (post and "POST" or "GET") + url)
            if post:
                res = self.session.post(url, **kwargs).content
            else:
                res = self.session.get(url, timeout=self.time_out, **kwargs).content
            return res
        except Exception as e:
            time.sleep(self.error_sleep_time)
            print_msg(("Download exception:", str(e)))
            try_times += 1
            if try_times < 3:
                print_msg("Retrying ...")
                return self.download(url, method, try_times, **kwargs)
            else:
                return None
