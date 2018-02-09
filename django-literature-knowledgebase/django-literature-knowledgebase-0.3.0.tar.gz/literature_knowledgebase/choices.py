# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices


SOURCES = Choices(
    (0, 'pubmed', _('pubmed')),
    (1, 'pmc', _('pmc')),
)
