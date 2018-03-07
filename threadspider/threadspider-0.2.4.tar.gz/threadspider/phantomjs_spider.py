# coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/8/25.
# ---------------------------------
from Queue import Queue
from threading import Thread
import urllib2
import time
import datetime
import random
from utils.encrypt import md5
from selenium import webdriver
import os
import psutil
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
import urlparse
from pybloom import BloomFilter

_queue = Queue(500000)
_size = 0
webdriver_list = []

def phantomjs_spider_init(poolsize):
    print datetime.datetime.now(), "[PhantomJSSpider]:init...."
    global _size, _queue, _url_max_num
    if _size == 0:
        _size = poolsize

        def run():
            for i in range(0, _size):
                _ = webdriver.PhantomJS()
                webdriver_list.append(_)
                def work(_=_):
                    while 1:
                        fun = _queue.get()
                        if fun:
                            fun(_)
                        _queue.task_done()

                thread = Thread(target=work)
                thread.setDaemon(True)
                thread.start()

        run()


def phantomjs_spider_join():
    global _queue
    _queue.join()
    for i in webdriver_list:
        i.quit()
    self_pid = os.getpid()
    process = psutil.Process(pid=self_pid)
    for _ in process.children():
        if _.name() == "phantomjs":
            _.kill()


class PhantomjsSpider(object):
    _url_buff = None
    def __init__(self, url, charset=None,headers=None, response_handle=None, timeout=3, retry_times=30, load_wait=None,
                 execute_js=None, execute_js_wait=None,
                 retry_delta=3, http_proxy_url=None, force=False):
        '''
            url   目标url
            charset   编码
            data   post的数据,字符串
            headers  自定义请求头,dict
            response_handle 采集结果处理函数
            timeout  超时时间,int,  比如:3
            retry_times 重试次数,int,比如3
            load_wait  加载页面后等待时间,秒.
            execute_js  加载页面完成后执行的js
            execute_js_waite 执行js之后等待的时间
            retry_delta   如果出错,重试间隔,秒,int
            http_proxy_url         代理ip,  "http://192.168.1.1:80"
            force         强制爬取,而不管有没有爬取过.
        '''
        if not PhantomjsSpider._url_buff:
            PhantomjsSpider._url_buff = BloomFilter(500000000)
        global _queue
        _hash = md5(url)
        self.url = url
        self.timeout = timeout
        self.retry_times = retry_times
        self.retry_delta = retry_delta
        self.response_handle = response_handle
        self.charset = charset
        self.headers = headers
        self.execute_js = execute_js
        self.execute_js_wait = execute_js_wait
        self.load_wait = load_wait
        self.proxy = http_proxy_url
        if not force:
            if _hash not in PhantomjsSpider._url_buff:
                PhantomjsSpider._url_buff.add(_hash)
                _queue.put(self._go)
        else:
            _queue.put(self._go)

    def _go(self, brower):
        for i in range(0, self.retry_times):
            brower.set_page_load_timeout(self.timeout)
            dcap = DesiredCapabilities.PHANTOMJS.copy()
            if self.headers:
                for key, value in self.headers.items():
                    dcap['phantomjs.page.customHeaders.{}'.format(key)] = value
            if self.proxy:
                proxy_info = urlparse.urlparse(self.proxy)
                proxy_hostname = proxy_info.hostname
                if proxy_info.scheme == "http":
                    if not proxy_info.port:
                        proxy_port = 80
                    else:
                        proxy_port = int(proxy_info.port)
                    http_proxy = Proxy(
                        {
                            'proxyType': ProxyType.MANUAL,
                            'httpProxy': '%s:%s' % (proxy_hostname, proxy_port)  # 代理ip和端口
                        })
                    http_proxy.add_to_capabilities(dcap)
            brower.start_session(dcap)
            try:
                brower.get(self.url)
                if self.load_wait:
                    time.sleep(self.load_wait)
                if self.execute_js:
                    brower.execute_script(self.execute_js)
                if self.execute_js_wait:
                    time.sleep(self.execute_js_wait)
                data = brower.page_source
                if not isinstance(data, unicode) and self.charset:
                    data = data.decode(self.charset, errors="ignore")
                if self.response_handle:
                    self.response_handle(data)
            except Exception as e:
                print datetime.datetime.now(), "[PhantomJSSpider]:%s Exception:%s" % (self.url, e)
                time.sleep(self.retry_delta)
            else:
                print datetime.datetime.now(), "[PhantomJSSpider]:%s Success!" % self.url
                break
