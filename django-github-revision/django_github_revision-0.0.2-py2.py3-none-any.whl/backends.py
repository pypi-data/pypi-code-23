from dealer.auto import auto
from django.conf import settings


def dealer():
    return auto.revision


def auto():
    return getattr(settings, 'REVISION_ID', dealer())