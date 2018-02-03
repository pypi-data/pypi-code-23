# -*- coding: utf-8 -*-

"""
trading212api.api
~~~~~~~~~~~~~~

This module provides the main api.
"""

import re
import json
from requests import Session
from trading212api.datastruct import Account, Instrument
from trading212api._internal_utils import URLS, ENCOD, PARAMS, INSTRUMS
from trading212api.exceptions import *


class Client(object):
    """Interface with the service"""
    def __init__(self, mode='demo'):
        if mode not in ['demo', 'live']:  # check if acceptable
            raise ValueError("mode not acceptable")
        self.mode = mode                  # set mode (demo or live)
        self.session = Session()          # set session to mantain cookie
        self.account = Account(mode)      # init account
        self.positions = self.account.positions
        self.instruments = {'list': []}   # init instruments

    def login(self, username, password):
        """set up connection"""
        # ~ first connection to authenticate account
        payload = {PARAMS['username']: username,  # username field
                   PARAMS['password']: password}  # password field
        # make a post request with payload in body to authentication site
        response = self._post(URLS['auth'], data=payload)
        # ~ second connection to log in
        payload = response.json()['data']['parameters']  # forward parameters from authentication
        response = self._post(URLS['login'] % self.mode, data=payload)
        # find account id in response content (found in javascript array)
        account_id = int(re.search(r'(?<=accountId: )\d*', response.text).group(0))
        # ~ init account
        headers = {PARAMS['cont']: PARAMS['json'],
                   PARAMS['client']: 'accountId=%d' % account_id}
        # send request with account id in headers
        response = self._get(URLS['account'] % self.mode, headers=headers)
        self.account.update(response.json())

    def refresh(self):
        """update account data"""
        headers = {PARAMS['cont']: PARAMS['json'],
                   PARAMS['client']: 'accountId=%d' % self.account.id}
        # send request with account id in headers
        response = self._get(URLS['account'] % self.mode, headers=headers)
        self.account.update(response.json())

    def get_historical_data(self, instrum, num, time_span):
        """retrieve data from chart"""
        time_conv = {  # define a conversion table for time span
            '1m': "ONE_MINUTE",
            '5m': "FIVE_MINUTES",
            '10m': "TEN_MINUTES",
            '15m': "FIFTEEN_MINUTES",
            '30m': "THIRTY_MINUTES",
            '1h': "ONE_HOUR",
            '4h': "FOUR_HOURS",
            '1d': "ONE_DAY",
            '1w': "ONE_WEEK",
            '1m': "ONE_MONTH"}
        self._check_instrument(instrum)  # check instrument if acceptable
        if time_span not in time_conv.keys():  # caught exceptions
            raise ValueError("Time span %s not acceptable" % time_span)
        time_span = time_conv[time_span]
        headers = self._get_headers('DEFAULT')  # get the default pattern of headers
        paylaod = [{'limit': num, 'instCode': instrum, 'periodType': time_span, 'withFakes': True}]
        url = URLS['candles'] % self.mode  # complete url
        response = self._post(url, headers=headers, data=json.dumps(paylaod)).json()
        return response[0]['candles']

    def open_position(self, mode, instrum, quantity):
        """open a position"""
        self._check_instrument(instrum)  # check
        self.update_price(instrum)  # update price for security measures
        self.check_max_quantity(instrum, quantity)  # check if max quantity allow this
        headers = self._get_headers('DEFAULT')
        paylaod = {PARAMS['instr']: instrum, 'quantity': quantity, 'notify': "NONE",
                   PARAMS['trgprc']: self.instruments[instrum].price[mode]}
        response = self._post(URLS['open-pos'] % self.mode, headers=headers,
                              data=json.dumps(paylaod)).json()
        self.account.update(response['account'])  # update account with latest values

    def close_position(self, pos_id):
        """close a position with a given id"""
        # check if exists in positions ids
        if pos_id not in [pos.id for pos in self.account.positions]:
            raise ValueError("Position not found")
        url = URLS['close-pos'] % (self.mode, pos_id)  # mount url
        response = self._delete(url, headers=self._get_headers('DEFAULT')).json()
        self.account.update(response['account'])  # update account with latest values

    def update_price(self, instrums):
        """update the price of an instrument"""
        if isinstance(instrums, str):  # convert to list of one element
            instrums = [instrums]
        self._check_instrument(instrums)
        response = self._get(URLS['instrum-update'] % (self.mode, ENCOD[','].join(instrums))).json()
        for ind, instrum in enumerate(instrums):  # fetch response for every instrum
            # check a list for better performances (preferable to list comprehension)
            if instrum not in self.instruments['list']:  # if not initied yet
                self.instruments[instrum] = Instrument(instrum)
                self.instruments['list'].append(instrum)  # add to list
            self.instruments[instrum].update(response[ind])  # update values with index
        return self.instruments[instrum]

    def check_max_quantity(self, instrum, quantity):
        """check max quantity"""
        response = self._get(URLS['max-quant'] % (self.mode, instrum)).json()
        max_quant = response[0]['maxBuy']  # take buy for convention
        if quantity <= max_quant:
            return True
        else:
            return False

    def _post(self, url, **kwargs):
        response = self.session.post(url, **kwargs)
        self._check_status(response)  # check response from server
        return response

    def _get(self, url, **kwargs):
        response = self.session.get(url, **kwargs)
        self._check_status(response)  # check response from server
        return response

    def _delete(self, url, **kwargs):
        response = self.session.delete(url, **kwargs)
        self._check_status(response)  # check response from server
        return response

    def _get_headers(self, name):
        """get a pattern of headers"""
        headers = {  # define a dict containing all headers pattern
            'DEFAULT': {PARAMS['cont']: PARAMS['json'],
                        PARAMS['client']: 'accountId=%d' % self.account.id}}
        if name not in headers.keys():
            raise ValueError("%s not in headers patterns" % name)
        return headers[name]


    def _check_instrument(self, instrums):
        """check if intrument acceptable"""
        if isinstance(instrums, str):
            if instrums not in INSTRUMS:
                raise ValueError("Instrument not compatible")
        else:
            for instrum in instrums:
                if instrum not in INSTRUMS:
                    raise ValueError("Instruments not compatible")

    def _check_status(self, response):
        """check status code"""
        if response.status_code != 200:  # raise RequestError
            raise RequestError(response)
