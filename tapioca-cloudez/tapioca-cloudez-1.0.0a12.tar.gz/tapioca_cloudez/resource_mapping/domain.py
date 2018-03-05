# -*- coding: utf-8 -*-

DOMAIN_MAPPING = {
    'domain_list': {
        'resource': 'domain/',
        'docs': '',
        'methods': ['GET'],
    },
    'domain_get': {
        'resource': 'domain/{id}/',
        'docs': '',
        'methods': ['GET'],
    },
    'domain_create': {
        'resource': 'domain/',
        'docs': '',
        'methods': ['POST'],
    },
    'domain_update': {
        'resource': 'domain/{id}/',
        'docs': '',
        'methods': ['PUT'],
    },
    'domain_delete': {
        'resource': 'domain/{id}/',
        'docs': '',
        'methods': ['DELETE'],
    },
    'domain_available': {
        'resource': 'domain-available/',
        'docs': '',
        'methods': ['POST'],
    }
}
