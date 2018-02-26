# coding: utf-8

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LMSClient(object):
    def __init__(self):
        self.session = requests.Session()

    def login(self, id, pw):
        url = 'https://lms.pknu.ac.kr/ilos/lo/login.acl'
        headers = {
            'Referer': 'http://lms.pknu.ac.kr/ilos/main/member/login_form.acl',
        }
        data = {
            'returnURL': '',
            'challenge': '',
            'response': '',
            'usr_id': id,
            'usr_pwd': pw,
        }
        r = self.session.post(url, headers=headers, data=data, verify=False)

        return u'로그인 정보가 일치하지 않습니다' not in r.text

    def logout(self):
        url = 'http://lms.pknu.ac.kr/ilos/lo/logout.acl'
        headers = {
            'Referer': 'http://lms.pknu.ac.kr/ilos/main/main_form.acl',
        }
        r = self.session.get(url, headers=headers)

    def send_note(self, to, title, content):
        url = 'http://lms.pknu.ac.kr/ilos/message/insert_pop.acl'
        headers = {
            'Referer': 'http://lms.pknu.ac.kr/ilos/message/insert_pop_form.acl',
        }
        data = {
            'TITLE': title,
            'RECV_IDs': to + '^',
            'CONTENT': content,
            'encoding': 'utf-8',
        }
        r = self.session.post(
            url, headers=headers, data=data, allow_redirects=False)

        try:
            body = r.json()
        except ValueError:
            return False

        return not body['isError']
