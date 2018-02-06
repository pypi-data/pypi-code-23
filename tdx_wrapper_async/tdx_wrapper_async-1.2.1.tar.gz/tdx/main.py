# -*- coding:utf-8 –*-

from tdx.engine import Engine
import datetime
from tdx.utils.util import precise_round
import pandas as pd
import logbook
import threading
import timeit
import click


def process_quotes(quotes):
    quotes['change'] = quotes['price'] / quotes['last_close'] - 1
    quotes['up_limit'] = (quotes['last_close'] * 1.1).apply(precise_round) == quotes['price']
    quotes['down_limit'] = (quotes['last_close'] * 0.9).apply(precise_round) == quotes['price']
    quotes.sort_values('change', ascending=False, inplace=True)
    quotes.set_index('code', drop=False, inplace=True)
    block = pd.concat([engine.concept, engine.index, engine.fengge])
    quotes = block.set_index('code').join(quotes, how='inner')
    grouped = quotes.groupby('blockname').sum()[['up_limit', 'down_limit', 'amount']]
    print(grouped.sort_values('up_limit', ascending=False))


def minute_time_data():
    stock_list = engine.stock_list.index.tolist()

    now = datetime.datetime.now()

    for stock in stock_list:
        fs = engine.api.to_df(engine.api.get_minute_time_data(stock[0], stock[1]))
        # print(fs)

    print((datetime.datetime.now() - now).total_seconds())


def quotes():
    start_dt = datetime.datetime.now()
    quote = engine.stock_quotes()
    print(datetime.datetime.now() - start_dt).total_seconds()
    process_quotes(quote)


def main():
    logbook.StderrHandler().push_application()
    engine = Engine(best_ip=True, thread_num=1)
    with engine.connect():
        engine.get_k_data('000002', '20100921', '20100930', '1m')


def test_transaction():
    engine = Engine(best_ip=True, thread_num=1)
    with engine.connect():
        df = engine.get_k_data('000001', '20130601', '20171231', '1m')

        df = engine.get_security_bars(['000001', '000521'], '1d', start=pd.to_datetime('20180102'))


if __name__ == '__main__':
    engine = Engine(best_ip=True, thread_num=1)
    with engine.connect():
        print(engine.api.get_security_count(0))
        print(engine.api.get_security_count(1))
        lists = engine.stock_list
        print(engine.get_security_bars('300737', '1d', pd.to_datetime('20161201'), pd.to_datetime('20171231')))
        print(engine.get_k_data('300737', '20161201', '20171231', '1d'))
    print(timeit.timeit(test_transaction, number=1))
    # print(timeit.timeit(main, number=1))
