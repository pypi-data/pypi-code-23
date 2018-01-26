# -*- coding:utf-8 -*-

import re
import datetime
import urllib
import logging

try:
    from django.conf import settings
except ImportError:
    import config as settings

from .anti_config import db, Key, Pos, Host, Url

from .utils import get_normal_url, get_normal_quote, get_redis_key, check_redis_urls, wait_redis_urls


TODAY = datetime.date.today()
YANDEX_URL = 'http://yandex.ru/yandsearch?p=%d&text=%s&lr=%d'
GOOGLE_URL = 'https://www.google.ru/search?q=%s'

FORMAT = '[%(asctime)-15s] // %(message)s'
LEVEL = logging.DEBUG if getattr(settings, 'DEBUG', False) else logging.WARNING
logging.basicConfig(format=FORMAT, level=LEVEL)


class openYandexMixin():
    def load_yandex_cache_pos(self, phrase, lr=213, cache=True, depth=2):
        if not phrase:
            return
        phrase_quote = get_normal_quote(phrase)
        self.urls = [YANDEX_URL % (i, phrase_quote, lr) for i in xrange(depth)]
        if not check_redis_urls(self.rds, self.urls, prefix='formed') or not cache:
            for url in self.urls:
                logging.warning('Get data from browser: ' + url)
                redis_key = get_redis_key(self.rds, url, prefix='formed')
                self.rds.set(redis_key, '')
                self.run_task(url, app_id='formed')

    def get_yandex_cache_pos(self, phrase, lr=213, cache=True, depth=2, timeout=120):
        """ data = obj.get_yandex_cache_pos(phrase, lr?). Получим позиции по ключевой фразе(первые 100)"""
        if not phrase:
            return []
        self.load_yandex_cache_pos(phrase, lr, cache, depth)
        wait_redis_urls(self.rds, self.urls, timeout, prefix='formed')
        res = []
        for url in self.urls:
            logging.debug(url)
            data = self.get_data(url)['search']
            res += data
        return res

    def get_yandex_date_pos(self, phrase, date, lr=213):
        if not phrase:
            return []
        res = db.session.query(Pos.pos,
                               Key.key,
                               Host.host,
                               Url.url,
                               Pos.search,
                               Pos.lr)\
                        .join(Key).join(Host).join(Url)\
                        .filter(Key.key == phrase, Pos.date == date, Pos.lr == lr).all()
        return res

    def load_google_cache_pos(self, phrase):
        if not phrase:
            return
        phrase_quote = get_normal_quote(phrase)
        url = GOOGLE_URL % phrase_quote
        logging.warning('Get data from browser: ' + url)
        self.run_task(url, app_id='formed')

    def get_google_cache_pos(self, phrase, cache=True, timeout=120):
        if not phrase:
            return
        phrase_quote = get_normal_quote(phrase)
        url = GOOGLE_URL % phrase_quote
        logging.debug(url)
        res = self.get_data(url, cache=cache, timeout=timeout)['search']
        return res

    def clear_yandex_cache_pos(self, phrase, lr=213, depth=2):
        if not phrase:
            return
        phrase_quote = get_normal_quote(phrase)
        for i in xrange(depth):
            url = YANDEX_URL % (i, phrase_quote, lr)
            redis_key = get_redis_key(self.rds, url, prefix='formed')
            self.rds.set(redis_key, '')

    def clear_google_cache_pos(self, phrase):
        if not phrase:
            return
        phrase_quote = get_normal_quote(phrase)
        url = GOOGLE_URL % phrase_quote
        redis_key = get_redis_key(self.rds, url, prefix='formed')
        self.rds.set(redis_key, '')

    def pages_of_site_in_index_yandex(self, site, pages=None, link=None):
        """ Получение данных по страницам сайта в индексе yandex """
        if not site:
            return []
        if pages is None:
            pages = []
        if isinstance(site, unicode):
            site = site.encode('utf8')

        if not link:
            link = u'http://yandex.ru/yandsearch?text=host:%s | host:www.%s&lr=213'\
                % (urllib.quote_plus(site), urllib.quote_plus(site))
        logging.debug(link)
        soup = self.get_soup(link)
        blocks = soup.find_all(class_='serp-item')
        if blocks:
            for item in blocks:
                tlink = item.find('a', class_='path__item')
                if tlink and not item.find('div', text='Реклама') and u'serp-adv-item' not in item['class']:
                    host = get_normal_url(tlink.text)
                    if 'yandex.ru' not in host and 'infected?' not in host:
                        url = item.find('a', class_='organic__url').get('href')
                        title = item.find('a', class_='organic__url').text
                        desc = item.find('div', class_='organic__text')
                        desc = desc.text if desc else None
                        if url not in [i['url'] for i in pages]:
                            pages.append({'url': url, 'title': title, 'desc': desc})
                tlink = item.find('a', class_='path__item')

                if tlink and not item.find('div', text='Реклама'):
                    host = get_normal_url(tlink['href'])
                    if 'yandex.ru' not in host and 'infected?' not in host:
                        url = item.find('a', class_='organic__url').get('href')
                        title = item.find('a', class_='organic__url').text
                        desc = item.find('div', class_='organic__text')
                        desc = desc.text if desc else None
                        if url not in [i['url'] for i in pages]:
                            pages.append({'url': url, 'title': title, 'desc': desc})

        link = soup.find('a', class_='pager__item_kind_next')
        if link:
            link = 'http://yandex.ru' + link['href']
            self.pages_of_site_in_index_yandex(site, pages, link)
        return pages

    def pages_of_site_in_index_google(self, site, pages=None, start=0):
        """ Получение данных по страницам сайта в индексе google """
        if not site:
            return []

        if pages is None:
            pages = []

        if isinstance(site, unicode):
            site = site.encode('utf8')
        link = 'https://www.google.ru/search?num=100&start=%d&q=site:%s' % (start, urllib.quote_plus(site))
        soup = self.get_soup(link)

        # Добавляем данные со страницы
        for item in soup.find_all(class_='g'):
            url = item.find('h3', {'class': 'r'}).find('a')['href']
            title = item.find('h3', {'class': 'r'}).find('a').text
            desc = item.find('span', {'class': 'st'})
            desc = desc.text if desc else None
            pages.append({'url': url, 'title': title, 'desc': desc})

        # Проверяем следующую страницу из пагинатора
        test = re.search('Следующая', str(soup))
        if test:
            start += 100
            self.pages_of_site_in_index_google(site, pages, start)
        return pages

    def clear_redis(self):
        """ Очистить базу redis """
        for key in self.rds.keys():
            self.rds.delete(key)
