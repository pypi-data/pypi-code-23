import ccxt
import yaml


def open_coinbase(key, secret):
    from coinbase.wallet.client import Client

    class Coinbase(object):

        def __init__(self):
            self.client = Client(key, secret)

        def fetch_balance(self):
            total = {}
            for account in self.client.get_accounts()["data"]:
                balance = account["balance"]
                total[balance["currency"]] = float(balance["amount"])
            return {'total': total}

    return Coinbase()


def open_exchange(class_name, key, secret, uid):
    if class_name == 'coinbase':
        return open_coinbase(key, secret)
    klass = getattr(ccxt, class_name)
    credentials = {
        'apiKey': key,
        'secret': secret
    }
    if uid is not None:
        credentials['uid'] = str(uid)
    return klass(credentials)


def load_exchanges(yaml_file):
    exchange_balances = {}
    with open(yaml_file, 'rb') as f:
        config = yaml.load(f.read())
        for exchange in config:
            class_name = exchange['name']
            alias = exchange.get('alias', exchange['name'])
            try:
                instance = open_exchange(class_name,
                                         exchange['key'],
                                         exchange['secret'],
                                         exchange.get('uid'))

                balances = instance.fetch_balance()['total']
                exchange_balances[alias] = {coin: q
                                            for coin, q in balances.items()
                                            if q != 0.0}
            except ccxt.ExchangeNotAvailable as ex:
                print ex.message

    return exchange_balances
