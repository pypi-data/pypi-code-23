from django.contrib import sitemaps
from django.core.urlresolvers import reverse
from . import models
from django.contrib.sitemaps import Sitemap
import datetime

class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    protocol = 'http'


    def items(self):
        return models.get_page_model().objects.filter(sitemap=True,members_only=False)

    def lastmod(self, obj):
        return obj.lastmod
