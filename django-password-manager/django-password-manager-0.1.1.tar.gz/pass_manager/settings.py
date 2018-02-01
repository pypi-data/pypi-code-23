from django.conf import settings

ACCOUNT_LOGOUT_URL = getattr(settings, 'ACCOUNT_LOGOUT_URL', '/logout/')
ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL = getattr(settings, 'ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL',
                                               '/password/reset/')

PASSWORD_REGEX = getattr(settings, 'PASSWORD_REGEX', '^(?=.*[A-Z])(?=.*[!@#$&*])(?=.*[0-9])(?=.*[a-z]).{6,}$')
STORE_PASSWORD_HISTORY = getattr(settings, 'STORE_PASSWORD_HISTORY', True)

# counts (Store user last 5 passwords)
PASSWORD_HISTORY_LIFE = getattr(settings, 'PASSWORD_HISTORY_LIFE', 24)

# in days
PASSWORD_EXPIRY_TIME = getattr(settings, 'PASSWORD_EXPIRY_TIME', 90)
