# -*- coding:utf-8 -*-

import re
import time
import urllib
import requests
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


from contextlib import contextmanager

from .anti_config import db


@contextmanager
def transaction():
    db.session.begin(nested=db.session.is_active)
    try:
        yield
    except:
        db.session.rollback()
        raise
    else:
        db.session.commit()


class TimeoutError(Exception):
    pass


def dict_of_array(arr, model, field):
    """ Создание новых элементов, на выходе словарь {field:id} """
    res = db.session.query(getattr(model, field)).filter(getattr(model, field).in_(arr)).all()
    res = {item[0] for item in res}
    [db.session.add(model(**{field: item})) for item in arr if item not in res and item]
    db.session.commit()
    data = db.session.query(getattr(model, field), getattr(model, 'id')).filter(getattr(model, field).in_(arr)).all()
    data = {item: item_id for item, item_id in data}
    return data


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def get_normal_url(url):
    url = url.strip().lower().replace('http://', '').replace('https://', '').replace('www.', '')
    if len(url) > 0:
        if url[-1] == '/':
            url = url[:-1]
        if len(url) < 20:
            url = url.encode('idna')
        return url[:255]
    return None


def get_normal_url_decode(url):
    url = url.strip().lower().replace('http://', '').replace('https://', '').replace('www.', '')
    if len(url) > 0:
        if url[-1] == '/':
            url = url[:-1]
        try:
            url = url.decode('idna')
        except:
            pass
        return url[:255]
    return None


def GetHash(query):
    SEED = "Mining PageRank is AGAINST GOOGLE'S TERMS OF SERVICE. Yes, I'm talking to you, scammer."
    Result = 0x01020345
    for i in range(len(query)):
        Result ^= ord(SEED[i % len(SEED)]) ^ ord(query[i])
        Result = Result >> 23 | Result << 9
        Result &= 0xffffffff
    return '8%x' % Result


def check_page(url):
    try:
        resp = requests.get('http://' + url, verify=False, timeout=120)
    except:
        try:
            resp = requests.get('http://www.' + url, verify=False, timeout=120)
        except:
            return False

    if resp.status_code == 200:
        return resp.text
    return False


def check_absolute_page(url):
    try:
        resp = requests.get(url, timeout=120)
        if resp.status_code == 200:
            return True
    except:
        pass
    return False


def remove_last_slash(link):
    if len(link) > 0:
        if link[-1] == '/':
            link = link[:-1]
    return link


def get_normal_quote(phrase):
    phrase = phrase.lower().strip()
    phrase_quote = urlparse.quote_plus(phrase)
    return phrase_quote


def parse_google_url(url):
    query = urlparse.parse_qs(urlparse.urlparse(url).query)
    if len(query.get('q')) > 0:
        return query.get('q')[0]
    return ''


def get_redis_key(rds, url, prefix='page'):
    keys = rds.keys(prefix + ':*:' + url)
    redis_key = keys[0] if keys else prefix + ':0:' + url
    return redis_key


def check_redis_urls(rds, urls, prefix='page'):
    for url in urls:
        keys = rds.keys(prefix + ':*:' + url)
        if not keys:
            return False
        if not rds.get(keys[0]):
            return False
    return True


def wait_redis_urls(rds, urls, timeout, prefix='page'):
    urls = urls if isinstance(urls, list) else [urls]
    now = time.time()
    while not check_redis_urls(rds, urls, prefix=prefix):
        time.sleep(0.3)
        if time.time() - now > timeout:
            raise TimeoutError
    return True


def parse_yandex(soup, query):
    data = []
    blocks = soup.find_all(class_='serp-item')
    if blocks:
        params = urlparse.parse_qs(query)
        key = params['text'][0]

        pos = int(params['p'][0]) * 50 if 'p' in params else 0
        lr = int(params['lr'][0]) if 'lr' in params else 0

        for item in blocks:
            tlink = item.find('a', class_='path__item')
            if tlink and not item.find('div', text='Реклама') and u'serp-adv-item' not in item['class']:
                host = get_normal_url(tlink.text)
                if 'yandex.ru' not in host and 'infected?' not in host:
                    pos += 1
                    try:
                        url = item.find('a', class_='organic__url').get('href')
                        data.append((pos, key.decode('utf8'), host, url, 0, lr, item.get('data-counter-block-id')))
                    except AttributeError:
                        pass

                    try:
                        url = item.find('a', class_='serp-item__title-link').get('href')
                        data.append((pos, key.decode('utf8'), host, url, 0, lr, item.get('data-counter-block-id')))
                    except AttributeError:
                        pass

    if len(blocks) == 0:
        if str(soup).find(u'По вашему запросу ничего не нашлось') == -1:
            return []
        if not blocks:
            return []
        return False

    return data


def parse_google(soup, query):
    data = []
    params = urlparse.parse_qs(query)
    if len(params['q']) == 0:
        return []
    key = params['q'][0]
    pos = int(params['start'][0]) if 'start' in params else 0

    for item in soup.find_all(class_='g'):
        pos += 1
        if item.find('cite'):
            res = re.search(r'(https://)?(www.)?([^/\ ]+)', item.find('cite').text)
            if res:
                host = get_normal_url(res.group())
                data.append((pos, key.decode('utf8'), host, None, 1, None))
    return data
