# -*- coding: utf-8 -*-
from django.db import models


class ArticleQuerySet(models.QuerySet):

    def fast(self):
        return self.select_related('user').all()
