# -*- coding: utf-8 -*-
from django.contrib.sitemaps import Sitemap

from ..models import JobCategory, JobOpening


class JobOpeningCategoriesSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return JobCategory.objects.all()


class JobOpeningSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return JobOpening.objects.active()

    def lastmod(self, obj):
        return obj.publication_start
