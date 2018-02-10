from __future__ import absolute_import, unicode_literals

from celery import shared_task

from . import load_lau as _load_lau, load_nuts as _load_nuts


@shared_task
def load_lau(code):
    return _load_lau(code)


@shared_task
def load_nuts(code):
    return _load_nuts(code)
