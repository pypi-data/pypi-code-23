# coding: utf-8
from pprint import pprint
from datetime import datetime, timedelta
try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse
import requests


def _get_all_pages(attr_data, *attrs):
    def wrapper(f):
        def func(self, *args, **kwargs):
            offset = kwargs.get('offset', 0)
            limit = kwargs.get('limit', 100)

            kwargs['offset'] = offset
            kwargs['limit'] = limit

            obj = f(self, *args, **kwargs)
            
            result = []
            result.extend(obj[attr_data])
            
            rows = obj['count']
            while rows > offset + limit:
                offset += limit
                kwargs['offset'] = offset
                
                obj = f(self, *args, **kwargs)
                result.extend(obj[attr_data])

            return result

        return func

    return wrapper


class ApiError(Exception):
    """Basic exception for errors raised by Yandex Webmaster"""


class YandexWebmaster(object):

    API_BASE = 'https://api.webmaster.yandex.net/v3/user/'
    API_USER = ''

    def __init__(self, client_token=None):
        self.CLIENT_TOKEN = client_token
        self.auth_header = {'Authorization': 'OAuth {}'.format(self.CLIENT_TOKEN)}
        self.hosts = {}
        self.status_code = None

        # https://api.webmaster.yandex.net/v3/user/{user-id}/hosts/
        self.API_USER = '{}{}/hosts/'.format(self.API_BASE, self.get_user_id())


    def request(self, method, url, params=None, data=None):
        r = requests.request(method, url, headers=self.auth_header, timeout=60*10, params=params, data=data)
        # print(r.url)
        self.status_code = r.status_code
        data = r.json()
        if r.status_code != 200:
            error = '{}: {}'.format(data['error_code'], data['error_message'])
            raise ApiError(error)
        return data

    def get(self, url, params=None):
        return self.request('GET', url, params=params)

    def post(self, url, data=None):
        return self.request('POST', url, data=data)

    def delete(self, url, data=None):
        return self.request('DELETE', url, data=data)

    def _get_hosts(self):
        for item in self.get_hosts():
            if item['verified']:
                host = urlparse(item['unicode_host_url']).netloc
                self.hosts[host] = item['host_id']
        return self.hosts

    def host(self, host):
        if not self.hosts:
            self._get_hosts()
        try:
            return self.hosts[host]
        except:
            raise ApiError('Site for found')

    def _date(self, date_from, date_to):
        # 2000-07-01T00:00:00+00:00
        if not date_from:
            date_from = datetime.now() - timedelta(days=30)

        if not date_to:
            date_to = datetime.now()

        date_from = date_from.strftime('%Y-%d-%mT%H:%M:00+00:00')
        date_to = date_to.strftime('%Y-%d-%mT%H:%M:00+00:00')
        return (date_from, date_to)

    def get_user_id(self):
        return self.get(self.API_BASE)['user_id']

    def add_host(self, url):
        return self.post(self.API_USER, {'host_url': url})

    def delete_host(self, host_id):
        return self.delete(self.API_USER + host_id + '/')

    def get_hosts(self):
        return self.get(self.API_USER)['hosts']

    def check_verification(self, host_id):
        return self.get(self.API_USER + host_id + '/')

    def verify_host(self, host_id, vtype):
        return self.post(self.API_USER + host_id + '/verification/?verification_type=' + vtype)

    def get_host_info(self, host_id):
        return self.get(self.API_USER + host_id + '/')

    def get_host_summary(self, host_id):
        return self.get(self.API_USER + host_id + '/summary/')
    
    def get_host_owners(self, host_id):
        return self.get(self.API_USER + host_id + '/owners/')

    def get_host_sitemaps(self, host_id):
        return self.get(self.API_USER + host_id + '/sitemaps/')

    def get_host_user_sitemaps(self, host_id):
        return self.get(self.API_USER + host_id + '/user-added-sitemaps/')

    def add_sitemap(self, host_id, url):
        return self.post(self.API_USER + host_id + '/user-added-sitemaps/', {'url': url})

    def delete_sitemap(self, host_id, sitemap_id):
        return self.delete(self.API_USER + host_id + '/user-added-sitemaps/' + sitemap_id + '/')

    def get_indexing_history(self, host_id, indexing_indicator=['DOWNLOADED', 'EXCLUDED', 'SEARCHABLE'], date_from='', date_to=''):
        # indexing_indicator=
        # SEARCHABLE	Страницы в поиске.
        # DOWNLOADED	Загруженные страницы.
        # DOWNLOADED_2XX	Страницы, загруженные с кодом из группы 2xx.
        # DOWNLOADED_3XX	Страницы, загруженные с кодом из группы 3xx.
        # DOWNLOADED_4XX	Страницы, загруженные с кодом из группы 4xx.
        # DOWNLOADED_5XX	Страницы, загруженные с кодом из группы 5xx.
        # FAILED_TO_DOWNLOAD	Не удалось загрузить.
        # EXCLUDED	Исключенные страницы.
        # EXCLUDED_DISALLOWED_BY_USER	Исключенные по желанию владельца ресурса (4xx-коды, запрет в robots.txt).
        # EXCLUDED_SITE_ERROR	Исключенные из-за ошибки на стороне сайта.
        # EXCLUDED_NOT_SUPPORTED	Исключенные из-за отсутствия поддержки на стороне роботов Яндекса.

        (date_from, date_to) = self._date(date_from, date_to)
        return self.get(self.API_USER + host_id + '/indexing-history/', {'indexing_indicator': indexing_indicator})['indicators']

    def get_tic_history(self, host_id, date_from='', date_to=''):
        (date_from, date_to) = self._date(date_from, date_to)
        return self.get(self.API_USER + host_id + '/tic-history/')['points']

    def get_popular_queries(self, host_id, order_by='TOTAL_CLICKS', indicator=['TOTAL_SHOWS', 'TOTAL_CLICKS', 'AVG_SHOW_POSITION', 'AVG_CLICK_POSITION']):
        # order_by=
        # TOTAL_SHOWS	Количество показов.
        # TOTAL_CLICKS	Количество

        # query_indicator=
        # TOTAL_SHOWS	Количество показов.
        # TOTAL_CLICKS	Количество кликов.
        # AVG_SHOW_POSITION	Средняя позиция показа.
        # AVG_CLICK_POSITION	Средняя позиция клика.
        
        return self.get(self.API_USER + host_id + '/search-queries/popular/', {'order_by': order_by, 'query_indicator':indicator})


    def get_external_links_history(self, host_id, indicator='LINKS_TOTAL_COUNT'):
        return self.get(self.API_USER + host_id + '/links/external/history/', {'indicator': indicator})
        
    @_get_all_pages('links')
    def get_external_links(self, host_id, offset=0, limit=100):
        return self.get(self.API_USER + host_id + '/links/external/samples/', {'offset': offset, 'limit':limit})

    @_get_all_pages('original_texts')
    def get_original_texts(self, host_id, offset=0, limit=100):
        return self.get(self.API_USER + host_id + '/original-texts/', {'offset': offset, 'limit':limit})

    def add_original_text(self, host_id, content):
        return self.post(self.API_USER + host_id + '/original-texts/', {'content': content})

    def delete_original_text(self, host_id, text_id):
        return self.delete(self.API_USER + host_id + '/original-texts/' + text_id + '/')


def main():
    token = 'M1bNXqEKl3rCp64XrPb8WW5GckFXnyNZdMAY16w'
    y = YandexWebmaster(client_token=token)

    print(y.get_hosts())
    
    host_id = y.host('site.com')
    #host_id = 'http:site.com:80'
    
    print(y.get_host_summary(host_id))
    print(y.get_indexing_history(host_id))
    print(y.get_tic_history(host_id))
    print(y.get_popular_queries(host_id))
    print(y.get_external_links(host_id))
   

if __name__ == '__main__':
    main()