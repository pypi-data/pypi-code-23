try:
    from django.urls import reverse  # Added in Django 1.10
except ImportError:
    from django.core.urlresolvers import reverse
