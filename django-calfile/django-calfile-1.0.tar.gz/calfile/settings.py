from django.conf import settings

CALFILE_DATE_FORMAT = getattr(settings, 'CALFILE_DATE_FORMAT', '%d-%m-%Y %H:%M')
