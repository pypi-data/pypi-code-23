

import urllib
import requests
import json
import re
import os
import time
from abs import AbstractApi

'''
f = fl3.File(domain='flamingo.exem-oss.org')
f.login('user', 'pw')
f.delete('/user/hive/password/README.md')
f.upload_file('README.md', '/user/hive/password/README.md')

# TO BE
f.chmod('/user/hive/password/README.md', '755')
f.chown('/user/hive/password/README.md', 'hdfs:hdfs')
'''

COOKIE_FILE = os.path.join(str(os.getenv("HOME")), '.fladm_cookie.json')


class Auth(AbstractApi):
    def __init__(self):
        pass

    domain = 'flamingo.exem-oss.org'
    cookie = None
    expired = None

    def exits_cookie(self):
        return os.path.exists(COOKIE_FILE)

    def validate(self):
        if self.exits_cookie():
            self.load_cookie()
            now = time.time()

            if now > self.expired:
                return False

        return bool(re.match('JSESSIONID=[a-zA-Z_0-9]{32}', self.cookie))

    def save_cookie(self):
        f = open(COOKIE_FILE, 'w')
        f.write(json.dumps({
            'domain': self.domain,
            'cookie': self.cookie,
            'expired': time.time() + 600
        }))
        f.close()

    def load_cookie(self):
        f = open(COOKIE_FILE, 'r')
        o = json.loads(f.read())
        self.domain = o['domain']
        self.cookie = o['cookie']
        self.expired = o['expired']

    def login(self, domain, username, password):
        self.domain = domain

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            # 'Content-Length': '28',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': self.domain,
            'Origin': 'http://%s' % self.domain,
            'Pragma': 'no-cache',
            'Referer': 'http://%s/login' % self.domain,
            # 'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }

        url = 'http://%s/login' % self.domain

        data = urllib.urlencode({
            'username': username,
            'password': password
        })

        s = requests.session()
        s.headers.update(headers)

        s.get(url)
        r = s.post(url, data=data, allow_redirects=False)

        cookie = 'JSESSIONID=%s' % r.cookies.get('JSESSIONID')

        # set cookie to server
        headers['Cookie'] = cookie
        s.headers.update(headers)
        s.get(url)

        self.cookie = cookie
        return cookie
