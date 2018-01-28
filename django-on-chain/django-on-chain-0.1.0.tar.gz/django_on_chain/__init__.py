from django.conf import settings

SETTINGS = {
    'DEFAULT_TIMEOUT': 10,
    'REFORMAT_ALL_ERRORS': True,
}

SETTINGS.update(getattr(settings, 'DJANGO_ON_CHAIN', {}))
