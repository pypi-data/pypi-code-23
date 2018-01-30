import os
from django.conf import settings

ONIVORO_DATA_ROOT = os.path.join(settings.BASE_DIR, "..", "..", "onivoro", "downloads")
ONIVORO_MAIL_NOTIFY = True
ONIVORO_MAIL_RECIPIENTS = None
ONIVORO_MAIL_SENDER = None