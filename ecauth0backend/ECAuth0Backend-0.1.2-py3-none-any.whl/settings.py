from django.conf import settings

AUTH0_DOMAIN = getattr(settings, 'AUTH0_DOMAIN', None)

AUTH0_CLIENT_ID = getattr(settings, 'AUTH0_CLIENT_ID', None)
AUTH0_CLIENT_SECRET = getattr(settings, 'AUTH0_CLIENT_SECRET', None)
AUTH0_CALLBACK_URL = getattr(settings, 'AUTH0_CALLBACK_URL', None)

AUTH0_JWT_SECRET = getattr(settings, 'AUTH0_JWT_SECRET', None)
AUTH0_JWT_CLIENT_ID = getattr(settings, 'AUTH0_JWT_CLIENT_ID', None)
AUTH0_JWT_HEADER_SEPARATOR = getattr(settings, 'AUTH0_JWT_HEADER_SEPARATOR', 'JWT')

AUTH0_BACKEND_SUCCESS_REDIRECT = getattr(settings, 'AUTH0_BACKEND_SUCCESS_REDIRECT', '/success/')
AUTH0_BACKEND_FAILURE_REDIRECT = getattr(settings, 'AUTH0_BACKEND_FAILURE_REDIRECT', '/failed/')
AUTH0_BACKEND_CALLBACK_URL = getattr(settings, 'AUTH0_BACKEND_CALLBACK_URL', r'^auth_callback/$')
