# -*- coding: utf-8 -*-

"""
trading212api.datastruct
~~~~~~~~~~~~~~

This module provides the data structures needed by client.
"""


class Account(object):
    """represent the account datas"""
    # at the moment this data structure is very basic and need any func, namespace
    def __init__(self, mode):
        self.mode = mode
        self.positions = []

    def update(self, raw_data):
        self.id = raw_data['id']  # account id
        self.positions.clear()  # clear positions
        for pos in raw_data['positions']:  # convert every raw position
            self.positions.append(Position(pos))
        self.funds = {  # cash avaible
            'free': raw_data['cash']['free'],
            'total': raw_data['cash']['total'],
            'result': raw_data['cash']['ppl'],  # actual results
        }


class Instrument(object):
    """Instrument store class"""
    def __init__(self, name):
        self.name = name

    def update(self, raw_data):
        self.price = {'buy': raw_data['buy'], 'sell': raw_data['sell']}


class Position(object):
    """position store class"""
    def __init__(self, raw_data):
        self.id = raw_data['positionId']
        self.price = raw_data['averagePrice']
        self.instrument = raw_data['code']
        self.quantity = raw_data['quantity']
        self.margin = raw_data['margin']
        self.result = raw_data['ppl']
