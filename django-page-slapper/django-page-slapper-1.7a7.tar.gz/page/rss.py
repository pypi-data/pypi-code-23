import re
import feedparser
from django.core.cache import cache
from django.template import RequestContext
from django.template.loader import render_to_string

re_rss = re.compile('display="rss"')
re_feed = re.compile('feed="([^"]*)"')
re_max_results = re.compile('max_results="([^"]*)"')
re_headers_only = re.compile('headers_only')

import hashlib

cache_expire = 60 * 60 * 1  # one hour


def get(comment, request):
    """Takes comment and replaces any news tags with the news"""
    # news_tags = soup.findAll(name="news")
    max_results = 3

    if re_rss.search(comment):
        key = hashlib.md5(comment.encode('utf-8')).hexdigest()
        if not request.GET.get('refresh'):
            # try to get cache
            result = cache.get(key, None)
            if result:
                return result

        # re_max_results
        max_results_re_result = re_max_results.search(comment)
        if max_results_re_result:
            max_results = int(max_results_re_result.group(1))

        # include
        feed_re = re_feed.search(comment)
        if feed_re:
            template_values = {}
            template_values['feed'] = feedparser.parse(feed_re.group(1)).entries[:max_results]

            if re_headers_only.search(comment):
                template_values['headers_only'] = False
            else:
                template_values['headers_only'] = False

            response = render_to_string('page/rss.html', template_values)
            cache.set(key, response, cache_expire)
            return response
