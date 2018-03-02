"""Singular API Client settings. Should not be modified
SINGULAR_URL: Default Sigular API URL, if none is provided when constructing Client
ENDPOINTS: Singular API endpoints to be called when invoking Client methods"""

SINGULAR_URL = "http://qtaski.websensa.com/"

ENDPOINTS = {
    'example_method': {
        'url': 'example/',
        'method': 'POST'
    },
    'ping': {
        'url': 'api/ping/',
        'method': 'GET'
    }
}