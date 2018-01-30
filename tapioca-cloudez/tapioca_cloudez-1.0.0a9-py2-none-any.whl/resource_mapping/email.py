# -*- coding: utf-8 -*-

EMAIL_MAPPING = {
    'email_list': {
        'resource': 'email/',
        'docs': '',
        'methods': ['GET'],
    },
    'email_get': {
        'resource': 'email/{id}/',
        'docs': '',
        'methods': ['GET'],
    },
    'email_create': {
        'resource': 'email/',
        'docs': '',
        'methods': ['POST'],
    },
    'email_update': {
        'resource': 'email/{id}/',
        'docs': '',
        'methods': ['PUT'],
    },
    'email_delete': {
        'resource': 'email/{id}/',
        'docs': '',
        'methods': ['DELETE'],
    },
}
