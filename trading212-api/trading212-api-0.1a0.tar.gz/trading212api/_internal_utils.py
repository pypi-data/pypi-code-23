# -*- coding: utf-8 -*-

"""
trading212api._internal_utils
~~~~~~~~~~~~~~

This module provides utils used local.
"""

URLS = {
    'auth': "https://www.trading212.com/en/authenticate",
    'login': "https://%s.trading212.com/login",  # replacement with mode
    'account': "https://%s.trading212.com/rest/v2/account",
    'open-pos': "https://%s.trading212.com/rest/v2/trading/open-positions",
    'close-pos': "https://%s.trading212.com/rest/v2/trading/open-positions/close/%s",
    'instrum-update': "https://%s.trading212.com/rest/v1/prices?instrumentCodes=%s&withFakes=true",
    'max-quant': "https://%s.trading212.com/rest/v2/max-quantities?instrumentCodes=%s",
    'candles': "https://%s.trading212.com/charting/rest/v2/candles",
}

ENCOD = {
    ',': "%2C"
}

PARAMS = {
    'username': 'login[username]',
    'password': 'login[password]',
    'client': 'X-Trader-Client',
    # for laziness
    'instr': "instrumentCode",
    'trgprc': "targetPrice",
    'cont': "Content-Type",
    'json': "application/json",
}

INSTRUMS = ['EURUSD', 'EURUSD_ZERO', 'GBPUSD', 'GBPUSD_ZERO', 'USDCAD', 'USDCAD_ZERO', 'USDCHF',
            'USDCHF_ZERO', 'USDJPY', 'USDJPY_ZERO']
