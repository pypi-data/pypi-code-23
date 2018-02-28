# coding=utf-8
import requests
from selenium import webdriver


def get_headless_chrome():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    return webdriver.Chrome(chrome_options=chrome_options)


def form_browser_headers():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', 'Content-Type': 'application/x-www-form-urlencoded;',
        'Upgrade-Insecure-Requests': '1', 'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'}
    return headers


def fake_browser():
    return requests.Session()


if __name__ == '__main__':
    browser = fake_browser()
    headers = form_browser_headers()
    browser.get("http://A0000051.casmart.com.cn", headers=headers)
    response = browser.get("http://A0000277.casmart.com.cn/IndexHandler.ashx?action=HomeProduct&showNum=16&timer=0.4323412121412289")
    print response.text
