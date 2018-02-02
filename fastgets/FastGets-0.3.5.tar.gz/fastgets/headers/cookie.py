# coding: utf8

import os
import collections
import random
from ..core.errors import NoCookiesError


class CookieHelper(object):

    def __init__(self):
        self.domain_cookies_list_dict = collections.defaultdict(list)

    def load(self):
        from .. import env

        if not env.COOKIES_DIR:
            return

        for _, _, file_names in os.walk(env.COOKIES_DIR):
            for file_name in file_names:
                with open(env.COOKIES_DIR+file_name) as f:
                    for l in f:
                        if not l.strip():
                            continue
                        self.domain_cookies_list_dict[file_name].append(l)

    def random_choice(self, domain):
        cookies_list = self.domain_cookies_list_dict[domain]
        if not cookies_list:
            raise NoCookiesError
        return random.choice(cookies_list)


cookie_helper = CookieHelper()
cookie_helper.load()
