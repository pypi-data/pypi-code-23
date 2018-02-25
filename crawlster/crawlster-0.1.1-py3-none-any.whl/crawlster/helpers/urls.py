import urllib.parse

from crawlster.config import ListOption
from crawlster.helpers.base import BaseHelper


class UrlsHelper(BaseHelper):
    """Helper that provides shortcuts to various url operations"""
    name = 'urls'
    config_options = {
        'urls.allowed_domains': ListOption(default=lambda: []),
        'urls.forbidden_domains': ListOption(default=lambda: [])
    }

    def __init__(self):
        super(UrlsHelper, self).__init__()
        self.already_seen = set()
        self.forbidden_domains = []
        self.allowed_domains = []

    def initialize(self):
        self.allowed_domains = self.config.get('urls.allowed_domains')
        self.forbidden_domains = self.config.get('urls.forbidden_domains')

    def join(self, base, *parts):
        """Joins multiple url parts with the base.

        Note:
            if any part is an absolute url, it will overwrite the parts from
            before it.
        """
        res = base
        for part in parts:
            res = urllib.parse.urljoin(res, part)
        return res

    def mark_seen(self, url):
        """Marks an url as seen"""
        self.already_seen.add(url)

    def seen(self, url):
        """Returns whether the url was previously marked as seen or not"""
        return url in self.already_seen

    def multi_join(self, base, paths):
        """Given a base of urls and a list of paths, returns a list of
        joined urls
        """
        return [self.join(base, path) for path in paths]

    def get_hostname(self, url):
        """Returns only the hostname of the url (domain and subdomains)."""
        return urllib.parse.urlparse(url).netloc

    def get_base(self, url):
        return self.join(url, '/')

    def get_path(self, url):
        """Returns the URL path for the url"""
        return urllib.parse.urlparse(url).path

    def urlencode(self, data):
        """Creates a query string from data"""
        return urllib.parse.urlencode(data)

    def can_crawl(self, url, unique=False):
        if unique:
            if self.seen(url):
                return False
        hostname = self.get_hostname(url)
        if self.forbidden_domains and hostname in self.forbidden_domains:
            return False
        if self.allowed_domains and hostname not in self.allowed_domains:
            return False
        return True

    def has_extension(self, url, extensions):
        for ext in extensions:
            if url.endswith(ext):
                return True
        return False
