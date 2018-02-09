# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

from . import choices, managers


class Article(TimeStampedModel):
    """Article from NCBI. PubMed or PMC."""

    source = models.SmallIntegerField(
        choices=choices.SOURCES,
        default=choices.SOURCES.pubmed
    )
    identifier = models.IntegerField(db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, blank=True)
    comments = GenericRelation('user_activities.Comment')

    objects = managers.ArticleQuerySet.as_manager()

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        unique_together = ('source', 'identifier')

    def __str__(self):
        return '{0}: {1}'.format(self.get_source_display(), self.identifier)

    @property
    def article_url(self):
        base_url = 'http://www.ncbi.nlm.nih.gov/{0}'.format(self.get_source_display())

        if self.get_source_display() == 'pmc':
            return '{0}/articles/PMC{1}'.format(base_url, self.identifier)

        return '{0}/{1}'.format(base_url, self.identifier)

    @property
    def fetch_url(self):
        base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
        return '{0}?db={1}&id={2}'.format(base_url, self.get_source_display(), self.identifier)

    @property
    def summary_url(self):
        base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
        return '{0}?db={1}&id={2}&retmode=json'.format(base_url, self.get_source_display(), self.identifier)
