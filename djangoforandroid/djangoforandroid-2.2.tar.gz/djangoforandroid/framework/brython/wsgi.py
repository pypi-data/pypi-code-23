"""
WSGI config for brythonapp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

import sys

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "brythonapp.settings")

application = get_wsgi_application()
