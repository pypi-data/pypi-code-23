

import os
import urllib

import requests as rq
import random as rd
import datetime as dt
import ipywidgets as wg

from IPython.display import display, Image

from requests.packages.urllib3.exceptions import InsecureRequestWarning
rq.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Api_v1:
    """
    """

    def __init__(self,
                 interactive=False,
                 login=None,
                 path_secret='my_secret.txt',
                 update_token=False,
                 verbose=False
                 ):
        """
        """
        self._show_logo()

        self.interactive = interactive
        self.SG_LOGIN = login
        self.path_secret = os.path.join(os.path.expanduser('~'),
                                        path_secret)
        self.update_token = update_token
        self.verbose = verbose
        self.path_token = os.path.join(os.path.expanduser('~'),
                                       'my_token.txt')

        try:
            self._load_my_secret()
        except Exception:
            msg = 'Error extracting data from {}.\nThis file either does not exist or is not properly formatted.'
            msg = msg.format(self.path_secret)
            print(msg)
            self.create_sample_my_secret()
            return

        self.access_token_endpoint = self._get_uri()
        self.proxies = self._get_proxies()

        if not interactive:
            self.access_token = self._get_access_token()

        else:
            self.widget_input = self.create_widget_input()
            display(self.widget_input)

    def create_widget_input(self):
        """
        """
        login = wg.Text(description='Login :',
                        placeholder='your login',
                        value=self.SG_LOGIN,
                        layout=wg.Layout(width='400px'))
        pwd = wg.Password(description='Password : ',
                          placeholder='your password',
                          layout=wg.Layout(width='300px'))
        btn = wg.Button(description='Go',
                        layout=wg.Layout(width='100px'))
        status = wg.Text(value='Not logged',
                         disabled=True,
                         layout=wg.Layout(width='160px'))

        def _now():
            return dt.datetime.now().strftime('%H:%M:%S')

        def on_clicked(b):
            status.value = 'Last Logged: ' + _now()
            self.SG_LOGIN = login.value
            self.SG_PASSWORD = pwd.value
            self.access_token = self._get_access_token()

        btn.on_click(on_clicked)

        box = wg.HBox([login, pwd, btn, status], layout=wg.Layout(display='flex',
                                                                  justify_content='space-around',
                                                                  width='850px'))
        return box

    def _get_access_token(self):
        """
        """
        if not os.path.isfile(self.path_token) or self.update_token:
            return self._request_access_token()
        else:
            return self._load_access_token()

    def clear_secret_token(self):
        """
        """
        for path in [self.path_secret, self.path_token]:
            if os.path.isfile(path):
                os.remove(path)
                print('Deleted file {}'.format(path))

    @staticmethod
    def _show_secret(k, v):
        """
        """
        if 'PASSWORD' in k:
            # hidden = '*' * (len(v) - 2)
            hidden = ''
            if len(v) > 0:
                hidden = '*' * rd.randint(5, 40)
            v = v[:1] + hidden + v[-1:]
            return v
        return v

    @staticmethod
    def _show_token(t):
        """
        """
        n = 10
        n2 = int(n / 2)
        hidden = '*' * (len(t) - n)
        t = t[:n2] + hidden + t[-n2:]
        return t

    def _load_my_secret(self):
        """
        """
        with open(self.path_secret, 'r') as f:
            lines = f.readlines()
            lines = [e.replace(' ', '') for e in lines]
            lines = [e.split('\n')[0] for e in lines]
            lines = [e for e in lines if e != '']
            # exclude comments
            lines = [e for e in lines if not e.startswith('#')]

            if self.verbose:
                print('Variables in {}'.format(self.path_secret))
            for e in lines:
                k, v = e.split('=')
                if self.verbose:
                    print('{}={}'.format(k, self._show_secret(k, v)))
                setattr(self, k, v)

    def create_sample_my_secret(self):
        """
        """
        print('Sample file created. Contents:')
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here,
                            'sample',
                            'my_secret.txt')
        with open(path, 'r') as f:
            content = f.read()
            print('-' * 15)
            print(content)
            print('-' * 15)
        with open(self.path_secret, 'w') as f:
            f.write(content)
        print('Edit it with your own data.')

    def _load_access_token(self):
        """
        """
        with open(self.path_token, 'r') as f:
            access_token = f.read()
            if self.verbose:
                print('Access token {} loaded from file {}'.format(self._show_token(access_token),
                                                                   self.path_token))
        return access_token

    def _get_uri(self):
        """
        TBD
        """
        # external SG Connect v1
        url = 'https://login.sgmarkets.com/richclient/gettoken'
        if self.verbose:
            print('Token endpoint: {}'.format(url))
        return url

    def _get_proxies(self):
        """
        """
        try:
            rq.get('https://google.com')
            proxies = {}
        except:
            dic = {'login': self.PROXY_LOGIN,
                   'pwd': urllib.parse.quote(self.PROXY_PASSWORD),
                   'proxy_host': self.PROXY_HOST,
                   'proxy_port': self.PROXY_PORT}
            proxies = {
                'http': 'http://{login}:{pwd}@{proxy_host}:{proxy_port}'.format(**dic),
                'https': 'https://{login}:{pwd}@{proxy_host}:{proxy_port}'.format(**dic)
            }
        if self.verbose:
            print('proxies:', proxies)
        return proxies

    def _request_access_token(self):
        """
        TBD
        """
        params = {'Login': self.SG_LOGIN,
                  'Password': self.SG_PASSWORD,
                  'Application': 'SGM'}
        headers = {'Content-type': 'application/json'}
        proxies = self._get_proxies()
        r = rq.post(self.access_token_endpoint,
                    headers=headers,
                    params=params,
                    proxies=self.proxies,
                    verify=False)
        r.raise_for_status()
        content = r.json()

        if self.verbose:
            print(content)

        if not content['Success']:
            if self.interactive:
                self.widget_input.children[3].value = 'Wrong login/pwd'
            else:
                print('Wrong login/pwd')
            return

        assert content['TokenValue'], 'No TokenValue returned by SG Connect'
        access_token = content['TokenValue']

        if self.verbose:
            print('Access token {} saved to file {}'.format(self._show_token(access_token),
                                                            self.path_token))
        with open(self.path_token, 'w') as f:
            f.write(access_token)

        return access_token

    def get(self, url, payload=None):
        """
        """
        if payload is None:
            payload = {}
        headers = {'RC-Auth': self.access_token}
        r = rq.get(url,
                   headers=headers,
                   params=payload,
                   proxies=self.proxies)
        return r.json()

    def post(self, url, payload=None):
        """
        """

        headers = {'RC-Auth': self.access_token,
                   'Content-type': 'application/json'
                   }
        r = rq.post(url,
                    headers=headers,
                    json=payload,
                    proxies=self.proxies)
        return r.json()

    def _show_logo(self):
        """
        """
        url_image = 'https://gitlab.com/sgmarkets/sgmarkets-api-auth/raw/master/sgmarkets_api_auth/img/sg-research-logo-displayed.png'
        display(Image(url=url_image))
