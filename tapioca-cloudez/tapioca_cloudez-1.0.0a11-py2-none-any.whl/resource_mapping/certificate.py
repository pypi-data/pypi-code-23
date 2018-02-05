# -*- coding: utf-8 -*-

CERTIFICATE_MAPPING = {
    'certificate_list': {
        'resource': 'certificate/',
        'docs': '',
        'methods': ['GET'],
    },
    'certificate_get': {
        'resource': 'certificate/{id}/',
        'docs': '',
        'methods': ['GET'],
    },
    'certificate_create': {
        'resource': 'certificate/',
        'docs': '',
        'methods': ['POST'],
    },
    'certificate_update': {
        'resource': 'certificate/{id}/',
        'docs': '',
        'methods': ['PUT'],
    },
    'certificate_delete': {
        'resource': 'certificate/{id}/',
        'docs': '',
        'methods': ['DELETE'],
    },
}
