from dealer.auto import auto as dealer_auto
from django.conf import settings


def dealer():
    return dealer_auto.revision


def auto():
    return getattr(settings, 'REVISION_ID', dealer())