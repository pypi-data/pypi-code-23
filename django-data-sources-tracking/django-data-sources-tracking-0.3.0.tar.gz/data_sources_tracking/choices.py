# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices


FILE_TYPES = Choices(
    (0, 'tsv', _('tsv')),
    (1, 'csv', _('csv')),
    (2, 'txt', _('txt')),
    (3, 'vcf', _('vcf')),
    (4, 'bed', _('bed')),
    (5, 'bigwig', _('bigwig')),
    (6, 'wigfix', _('wigfix')),
    (7, 'chromatograms', _('chromatograms')),
    (8, 'other', _('other'))
)
