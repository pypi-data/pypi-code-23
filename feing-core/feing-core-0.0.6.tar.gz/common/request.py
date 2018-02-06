# -*- coding: UTF-8 -*-
from http import cookiejar
from urllib import request, error, parse

import requests
from selenium import webdriver

browserPath = 'D:/Python/phantomjs-2.1.1-windows/bin/phantomjs'


class RequestBuilder(object):
    def __init__(self):
        self.driver = webdriver.PhantomJS(executable_path=browserPath)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/54.0.2840.100 Safari/537.36 '
        }
        self.request_session = requests.session()

    def page_source(self, url):
        """
        使用selenium获取源码
        """
        self.driver.get(url)
        return self.driver.page_source

    def execute_source_script(self, js):
        """
        使用selenium执行js
        """
        return self.driver.execute_script(js)

    def get_with_cookie(self, url, retry_count=3, headers=None, proxies=None, data=None):
        """
        :param url: 请求 URL 链接
        :param retry_count: 失败重试次数
        :param headers: http header={'X':'x', 'X':'x'}
        :param proxies: 代理设置 proxies={"https": "http://12.112.122.12:3212"}
        :param data: urlencode(post_data) 的 POST 数据/json
        :return: 网页内容 | None
        """
        if url is None:
            return None
        if headers is None:
            headers = self.headers
        try:
            req = request.Request(url, headers=headers, data=data)
            cookie = cookiejar.CookieJar()
            cookie_process = request.HTTPCookieProcessor(cookie)
            opener = request.build_opener(cookie_process)
            if proxies:
                proxies = {parse.urlparse(url).scheme: proxies}
                opener.add_handler(request.ProxyHandler(proxies))
            html = opener.open(req).read()
        except error.URLError as e:
            print('>>>Request error:', e.reason)
            html = None
            if retry_count > 0:
                if hasattr(e, 'code') and 500 <= e.code < 600:
                    # retry when return code is 5xx HTTP erros
                    return self.get_with_cookie(url, retry_count - 1, headers, proxies, data)
        return html

    def get_with_session(self, url, retry_count=3, headers=None, proxies=None, data=None):
        """
        :param url: 请求 URL 链接
        :param retry_count: 失败重试次数
        :param headers: http header={'X':'x', 'X':'x'}
        :param proxies: 代理设置 proxies={"https": "http://12.112.122.12:3212"}
        :param data: urlencode(post_data) 的 POST 数据/json
        :return: 网页内容 | None
        """
        if headers:
            self.request_session.headers.update(headers)
        try:
            if data:
                html = self.request_session.post(url, data, proxies=proxies).content
            else:
                html = self.request_session.get(url, proxies=proxies).content
        except (ConnectionError, requests.Timeout) as e:
            print('>>>Request ConnectionError or Timeout:' + str(e))
            html = None
            if retry_count > 0:
                self.get_with_session(url, retry_count - 1, headers, proxies, data)
        except Exception as e:
            print('>>>Request Exception:' + str(e))
            html = None
        return html


def main():
    url = 'http://www.baidu.com'
    content = Request().get_with_cookie(url).decode('utf-8')
    print(str(content))

    content = Request().get_with_session(url).decode('utf-8')
    print(str(content))


if __name__ == '__main__':
    main()
