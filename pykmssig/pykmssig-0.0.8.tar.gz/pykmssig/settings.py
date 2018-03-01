from decouple import config


SIGNING_KEY_ALIAS = config('SIGNING_KEY_ALIAS', default='alias/pykmssig')
SIGNING_KEY_ACCOUNT_ID = config('SIGNING_KEY_ACCOUNT_ID', default=None)
