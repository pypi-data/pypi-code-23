# -*- coding: utf-8 -*-

MIGRATION_MAPPING = {
    'configr_migration': {
        'resource': 'configr-migration/',
        'docs': '',
        'methods': ['POST'],
    },
    'configr_migration_user': {
        'resource': 'configr-migration-user/',
        'docs': '',
        'methods': ['POST'],
    },
    'configr_migration_cloud': {
        'resource': 'configr-migration-cloud/',
        'docs': '',
        'methods': ['POST'],
    },
    'configr_migration_cloud_finish': {
        'resource': 'configr-migration-cloud/{id}/finish/',
        'docs': '',
        'methods': ['POST'],
    },
    'sync_list': {
        'resource': 'sync/',
        'docs': '',
        'methods': ['GET'],
    },
    'sync_get': {
        'resource': 'sync/{id}/',
        'docs': '',
        'methods': ['GET'],
    },
    'sync_create': {
        'resource': 'sync/',
        'docs': '',
        'methods': ['POST'],
    },
}
