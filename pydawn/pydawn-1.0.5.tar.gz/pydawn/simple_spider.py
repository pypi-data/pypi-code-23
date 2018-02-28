# coding=utf-8

from urlparse import urlparse
import re
import os
from browser_utils import fake_browser, form_browser_headers
import sys
from sqlite_utils import sqlite_get_db, sqlite_excute, sqlite_query
from string_utils import get_links, gen_md5

reload(sys)
sys.setdefaultencoding('utf-8')


def check_if_existed(conn, url_md5):
    # check url_md5 sql
    count_query = "SELECT COUNT(*) FROM URL WHERE url_md5='%s'" % url_md5
    for row in sqlite_query(conn, count_query):
        return row[0] > 0

    return False


def add_new_url(conn, urls):
    for url in urls:
        url_md5 = gen_md5(url)
        if check_if_existed(conn, url_md5):
            continue
        insert_sql = "INSERT INTO URL VALUES('%s', '%s', 0);" % (url, url_md5)
        print "add new url: %s" % url
        sqlite_excute(conn, insert_sql)


def set_url_status(conn, url_md5, status):
    update_sql = "UPDATE URL SET url_status=%d WHERE url_md5='%s';" % (status, url_md5)
    sqlite_excute(conn, update_sql)


def get_url_to_download(conn, count):
    count_query = "SELECT url FROM URL where url_status=0 LIMIT %d" % count
    urls = []
    for row in sqlite_query(conn, count_query):
        urls.append(row[0])
    return urls


def init_db(db_tag, reset_db):
    db_name = "%s.db" % db_tag
    if reset_db and os.path.exists(db_name):
        os.remove(db_name)
    conn = sqlite_get_db(db_name)
    create_table_sql = '''
                   CREATE TABLE IF NOT EXISTS URL
                   (url          TEXT     NOT NULL,
                   url_md5       TEXT     PRIMARY KEY NOT NULL,
                   url_status    INTEGER  NOT NULL
                    ) ;
                '''
    sqlite_excute(conn, create_table_sql)
    return conn


def simple_crawl(tag, host, seed_url, reset_db, call_back):
    conn = init_db(tag, reset_db)
    add_new_url(conn, seed_url)

    browser = fake_browser()
    headers = form_browser_headers()

    while True:
        urls = get_url_to_download(conn, 10)
        if len(urls) == 0:
            print "nothing todo, all job done!!!"
            break
        for url in urls:
            print "crawl url: %s" % url
            response = browser.get(url, headers=headers)
            new_urls = get_links(host, url, response.text)
            refined_urls = apply(call_back, (url, new_urls, response.text))
            add_new_url(conn, refined_urls)
            set_url_status(conn, gen_md5(url), 1)


if __name__ == '__main__':
    tag = "casmart"
    host = "casmart.com.cn"
    seed_url = ["http://www.casmart.com.cn/product/supplierlist.aspx"]
