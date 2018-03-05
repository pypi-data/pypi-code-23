# -*- coding: utf-8 -*-

WEBSITE_CRON_MAPPING = {
    'website_cron_list': {
        'resource': 'website-cron/',
        'docs': '',
        'methods': ['GET'],
    },
    'website_cron_get': {
        'resource': 'website-cron/{id}/',
        'docs': '',
        'methods': ['GET'],
    },
    'website_cron_create': {
        'resource': 'website-cron/',
        'docs': '',
        'methods': ['POST'],
    },
    'website_cron_update': {
        'resource': 'website-cron/{id}/',
        'docs': '',
        'methods': ['PUT'],
    },
    'website_cron_delete': {
        'resource': 'website-cron/{id}/',
        'docs': '',
        'methods': ['DELETE'],
    },
}
