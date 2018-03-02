import os
import sys

import django
from django.conf import settings

# We manually designate which settings we will be using in an environment variable
# This is similar to what occurs in the `manage.py`
sys.path.append(os.path.abspath(os.path.join('../../')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')


# `pytest` automatically calls this function once when tests are run.
def pytest_configure():
    settings.DEBUG = True
    # If you have any test specific settings, you can declare them here,
    # e.g.
    # settings.PASSWORD_HASHERS = (
    #     'django.contrib.auth.hashers.MD5PasswordHasher',
    # )
    # DATABASES = {
    #     "default": {
    #         "ENGINE": "django.db.backends.sqlite3",
    #         "NAME": ":memory:",
    #     }
    # }
    # EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    django.setup()
    # Note: In Django =< 1.6 you'll need to run this instead
    # settings.configure()
