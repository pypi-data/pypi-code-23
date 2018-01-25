"""
Database settings, used PostgreSQL without auth by default.
"""

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cms_qe',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'OPTIONS': {
            'application_name': 'cms_qe',
        }
    }
}
