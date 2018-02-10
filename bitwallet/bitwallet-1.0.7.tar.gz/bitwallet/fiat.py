import UserDict
import calendar

import requests


class UsdRates(UserDict.UserDict):

    def __init__(self, currencies, backup_rates={}, translations={}):
        UserDict.UserDict.__init__(self)
        translations_r = {v: k for k, v in translations.iteritems()}

        BATCH_SIZE = 4
        todo = currencies[:]
        while todo:
            batch = todo[:BATCH_SIZE]
            todo = todo[BATCH_SIZE:]

            rates = self._get_exchanges_now(translations.get(coin, coin)
                                            for coin in batch)
            self.update({translations_r.get(coin, coin): v
                         for coin, v in rates.iteritems()})

        for coin in set(backup_rates) - set(self.keys()):
            self[coin] = backup_rates[coin]

    @staticmethod
    def _get_exchanges_now(currencies):
        url_current = ("https://min-api.cryptocompare.com/data/price"
                       "?fsym=USD&tsyms=%s" % (",".join(currencies)))
        return requests.get(url_current).json()

    @staticmethod
    def _get_exchanges_at(at, currencies):
        '''
        Usage: self._get_exchanges_at(datetime.datetime.utcnow(), batch)
        '''
        ts = calendar.timegm(at.utctimetuple())

        url_historical = ("https://min-api.cryptocompare.com/data/pricehisto"
                          "rical?fsym=USD&tsyms=%s&ts=%d" %
                          (",".join(currencies), ts))

        return requests.get(url_historical).json()['USD']
