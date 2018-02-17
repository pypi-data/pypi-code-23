import requests
import delegator
import crayons
from bs4 import BeautifulSoup

session = requests.Session()

delegator.TIMEOUT = 600

class Video:

    def __init__(self, ph, title, url, category=None):
        self.ph = ph
        self.title = title
        self.url = url
        self.category = category
        self._meta = {}

    def __repr__(self):
        return "<Video title='{}'>".format(self.title)

    @property
    def meta(self):
        self._get_metadata()
        return self._meta

    def _get_metadata(self):
        soup = self.ph._get_bs(self.url)

        count = soup.find('span', class_='count').text
        self._meta['count'] = int(count.replace(',', ''))

        percent = soup.find('span', class_='percent').text[:-1]
        self._meta['percent'] = float('0.{}'.format(percent))

        try:
            cats = soup.find('div', class_='categoriesWrapper').text.split()[1:-2]
            self._meta['category_names'] = cats
        except AttributeError:
            self._meta['category_names'] = []

    def download(self, block=True):
        print(crayons.red('Downloading video…'))
        c = delegator.run('youtube-dl {}'.format(self.url), block=block)
        return c

class Category:
    def __init__(self, ph, title, url):
        self.ph = ph
        self.title = title
        self.url = url

    def __repr__(self):
        return "<Category title='{}'>".format(self.title)

    @property
    def id(self):
        try:
            return self.url.split('=')[1]
        except IndexError:
            return self.url.split('/')[-1]

    def __iter__(self):
        return (v for v in self.videos())

    def videos(self, max=None):

        def gen(url):
            soup = self.ph._get_bs(url)

            next = soup.find('li', class_='page_next').find('a')['href']

            for span in soup.find_all('span', class_='title'):

                if span.find('a'):
                    title = span.find('a')['title']
                    url = self.ph.base_url + span.find('a')['href']

                    yield Video(ph=self.ph, title=title, url=url, category=self)

            yield from gen(next)

        i = 0
        for v in gen(self.url):
            i += 1
            if max is None or i <= max:
                yield v
            else:
                break


class PornHub:
    def __init__(self):
        self.base_url = 'https://www.pornhub.com'

    def _get(self, url, *args, **kwargs):
        if not url.startswith('http'):
            url = '{}{}'.format(self.base_url, url)

        return session.get(url, *args, **kwargs)

    def _get_bs(self, url, *args, **kwargs):
        r = self._get(url, *args, **kwargs)
        return BeautifulSoup(r.content, 'lxml')

    def __getitem__(self, key):
        for cat in self.categories:
            if cat.title.lower() == key.lower():
                return cat

    def search(self, s, max=None):
        def gen(url):
            soup = self._get_bs(url, params={'search': s})
            next = soup.find('li', class_='page_next').find('a')['href']

            for span in soup.find_all('span', class_='title'):

                if span.find('a'):
                    title = span.find('a')['title']
                    url = self.base_url + span.find('a')['href']

                    yield Video(ph=self, title=title, url=url)

            yield from gen(next)

        i = 0
        for v in gen('/video/search'):
            i += 1
            if max is None or i <= max:
                yield v
            else:
                break

    @property
    def categories(self):

        soup = self._get_bs('/categories')

        categories = []

        for div in soup.find_all('div', class_='category-wrapper'):

            title = div.find('a')['alt']
            url = self.base_url + div.find('a')['href']

            c = Category(ph=self, title=title, url=url)

            categories.append(c)

        return categories

# for video in ph['college'].videos(max=25):
#     print(video.__dict__)