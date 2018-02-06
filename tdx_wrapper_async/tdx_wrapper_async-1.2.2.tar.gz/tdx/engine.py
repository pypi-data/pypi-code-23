# -*- coding:utf-8 –*-
from pytdx.hq import TdxHq_API
from pytdx.async.hq import ATdxHq_API
from pytdx.exhq import TdxExHq_API
from pytdx.params import TDXParams
from pytdx.util.best_ip import select_best_ip
from pytdx.reader import CustomerBlockReader, GbbqReader
from tdx.utils.util import fillna
import pandas as pd
from functools import wraps
import gevent
import traceback
from tdx.utils.memoize import lazyval
from six import PY2

import asyncio

from tdx.config import *

from logbook import Logger

logger = Logger('engine')


def stock_filter(code):
    if code[0] == 1:
        if code[1][0] == '6':
            return True
    else:
        if code[1].startswith("300") or code[1][:2] == '00':
            return True
    return False


class SecurityNotExists(Exception):
    pass


### return 1 if sh, 0 if sz
def get_stock_type(stock):
    one = stock[0]
    if one == '5' or one == '6' or one == '9':
        return 1

    if stock.startswith("009") or stock.startswith("126") or stock.startswith("110") or stock.startswith(
            "201") or stock.startswith("202") or stock.startswith("203") or stock.startswith("204"):
        return 1

    return 0


def retry(times=3):
    def wrapper(func):
        @wraps(func)
        def fun(*args, **kwargs):
            cls = args[0]
            count = 0
            while count < times:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    cls.connect()
                    count = count + 1

            raise Exception("connection failed after retried 3 times, please check your network")

        return fun

    return wrapper


class Engine:
    concurrent_thread_count = 50

    def __init__(self, *args, **kwargs):
        if 'ip' in kwargs:
            self.ip = kwargs.pop('ip')
        else:
            if kwargs.pop('best_ip', False):
                self.ip = self.best_ip
            else:
                self.ip = '14.17.75.71'
        if 'concurrent_thread_count' in kwargs:
            self.concurrent_thread_count = kwargs.pop('concurrent_thread_count', 50)
        self.thread_num = kwargs.pop('thread_num', 1)

        self.api = TdxHq_API(args, kwargs, raise_exception=True)

    def connect(self):
        self.api.connect(self.ip)
        return self

    def __enter__(self):
        return self

    def exit(self):
        self.api.disconnect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.disconnect()

    def quotes(self, code):
        code = [code] if not isinstance(code, list) else code
        code = self.security_list[self.security_list.code.isin(code)].index.tolist()
        data = [self.api.to_df(self.api.get_security_quotes(
            code[80 * pos:80 * (pos + 1)])) for pos in range(int(len(code) / 80) + 1)]
        return pd.concat(data)
        # data = data[['code', 'open', 'high', 'low', 'price']]
        # data['datetime'] = datetime.datetime.now()
        # return data.set_index('code', drop=False, inplace=False)

    def stock_quotes(self):
        code = self.stock_list.index.tolist()
        data = [self.api.to_df(self.api.get_security_quotes(
            code[80 * pos:80 * (pos + 1)])) for pos in range(int(len(code) / 80) + 1)]
        return pd.concat(data)

    @lazyval
    def security_list(self):
        return pd.concat(
            [pd.concat(
                [self.api.to_df(self.api.get_security_list(j, i * 1000)).assign(sse=0 if j == 0 else 1).set_index(
                    ['sse', 'code'], drop=False) for i in range(int(self.api.get_security_count(j) / 1000) + 1)],
                axis=0) for j
                in
                range(2)], axis=0)

    @lazyval
    def stock_list(self):
        aa = map(stock_filter, self.security_list.index.tolist())
        return self.security_list[list(aa)]

    @lazyval
    def best_ip(self):
        return select_best_ip()

    @lazyval
    def concept(self):
        return self.api.to_df(self.api.get_and_parse_block_info(TDXParams.BLOCK_GN))

    @lazyval
    def index(self):
        return self.api.to_df(self.api.get_and_parse_block_info(TDXParams.BLOCK_SZ))

    @lazyval
    def fengge(self):
        return self.api.to_df(self.api.get_and_parse_block_info(TDXParams.BLOCK_FG))

    @lazyval
    def block(self):
        return self.api.to_df(self.api.get_and_parse_block_info(TDXParams.BLOCK_DEFAULT))

    @lazyval
    def customer_block(self):
        return CustomerBlockReader().get_df(CUSTOMER_BLOCK_PATH)

    def xdxr(self, code):
        df = self.api.to_df(self.api.get_xdxr_info(self.get_security_type(code), code))
        if df.empty:
            return df
        df['datetime'] = pd.to_datetime((df.year * 10000 + df.month * 100 + df.day).apply(lambda x: str(x)))
        return df.drop(
            ['year', 'month', 'day'], axis=1).set_index('datetime')

    @lazyval
    def gbbq(self):
        df = GbbqReader().get_df(GBBQ_PATH).query('category == 1')
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d')
        return df

    def get_security_type(self, code):
        if code in self.security_list.code.values:
            return self.security_list[self.security_list.code == code]['sse'].as_matrix()[0]
        else:
            raise SecurityNotExists()

    @retry(3)
    def get_security_bars(self, code, freq, start=None, end=None, index=False):
        if index:
            exchange = self.get_security_type(code)
            func = self.api.get_index_bars
        else:
            exchange = get_stock_type(code)
            func = self.api.get_security_bars

        if start:
            start = start.tz_localize(None)
        if end:
            end = end.tz_localize(None)

        if freq in ['1d', 'day']:
            freq = 9
        elif freq in ['1m', 'min']:
            freq = 8
        else:
            raise Exception("1d and 1m frequency supported only")

        res = []
        pos = 0
        while True:
            data = func(freq, exchange, code, pos, 800)
            if not data:
                break
            res = data + res
            pos += 800

            if len(data) < 800:
                break

            if start and pd.to_datetime(data[0]['datetime']) < start:
                break
        try:
            df = self.api.to_df(res).drop(
                ['year', 'month', 'day', 'hour', 'minute'], axis=1)
            df['datetime'] = pd.to_datetime(df.datetime)
            df.set_index('datetime', inplace=True)
            if freq == 9:
                df.index = df.index.normalize()
        except ValueError:  # 未上市股票，无数据
            logger.warning("no k line data for {}".format(code))
            # return pd.DataFrame({
            #     'amount': [0],
            #     'close': [0],
            #     'open': [0],
            #     'high': [0],
            #     'low': [0],
            #     'vol': [0],
            #     'code': code
            # },
            #     index=[start]
            # )
            return pd.DataFrame()
        close = [df.close.values[-1]]
        if start:
            df = df.loc[lambda df: start <= df.index]
        if end:
            df = df.loc[lambda df: df.index.normalize() <= end]

        if df.empty:
            # return pd.DataFrame({
            #     'amount': [0],
            #     'close': close,
            #     'open': close,
            #     'high': close,
            #     'low': close,
            #     'vol': [0],
            #     'code': code
            # },
            #     index=[start]
            # )
            return df
        else:
            if int(df['vol'][-1]) <= 0 and end == df.index[-1] and len(df) == 1:  # 成交量为0，当天返回的是没开盘的数据
                return pd.DataFrame()
            df['code'] = code
            return df

    def _get_transaction(self, code, date):
        res = []
        start = 0
        while True:
            data = self.api.get_history_transaction_data(get_stock_type(code), code, start, 2000,
                                                         date)
            if not data:
                break
            start += 2000
            res = data + res

            if len(data) < 2000:
                break

        if len(res) == 0:
            return pd.DataFrame()
        df = self.api.to_df(res).assign(date=date)
        df.loc[0, 'time'] = df.time[1]
        df.index = pd.to_datetime(str(date) + " " + df["time"])
        df['code'] = code
        return df.drop("time", axis=1)

    def time_and_price(self, code):
        start = 0
        res = []
        exchange = self.get_security_type(code)
        while True:
            data = self.api.get_transaction_data(exchange, code, start, 2000)
            if not data:
                break
            res = data + res
            start += 2000

            if len(data) < 2000:
                break

        df = self.api.to_df(res)
        df.time = pd.to_datetime(str(pd.to_datetime('today').date()) + " " + df['time'])
        df.loc[0, 'time'] = df.time[1]
        return df.set_index('time')

    @classmethod
    def minute_bars_from_transaction(cls, transaction, freq):
        if transaction.empty:
            return pd.DataFrame()
        mask = transaction.index < transaction.index[0].normalize() + pd.Timedelta('12 H')

        def resample(transaction):
            if transaction.empty:
                return pd.DataFrame()
            data = transaction['price'].resample(
                freq, label='right', closed='left').ohlc()

            data['volume'] = transaction['vol'].resample(
                freq, label='right', closed='left').sum()
            data['code'] = transaction['code'][0]
            return data

        morning = resample(transaction[mask])
        afternoon = resample(transaction[~mask])
        if morning.empty and afternoon.empty:
            return pd.DataFrame()
        if not morning.empty:
            if not afternoon.empty:
                morning.index.values[-1] = afternoon.index[0] - pd.Timedelta('1 min')
            else:
                morning.index.values[-1] = morning.index.values[-1] + pd.Timedelta('90 min')

        df = pd.concat([morning, afternoon])

        return fillna(df)

    def _get_k_data(self, code, freq, sessions):
        trade_days = map(int, sessions.strftime("%Y%m%d"))
        if freq == '1m':
            freq = '1 min'

        if freq == '1d':
            freq = '24 H'

        res = []
        concurrent_count = self.concurrent_thread_count
        jobs = []
        for trade_day in trade_days:
            # df = Engine.minute_bars_from_transaction(self._get_transaction(code, trade_day), freq)
            reqevent = gevent.spawn(Engine.minute_bars_from_transaction, self._get_transaction(code, trade_day), freq)
            jobs.append(reqevent)
            if len(jobs) >= concurrent_count:
                gevent.joinall(jobs, timeout=30)
                for j in jobs:
                    if j.value is not None and not j.value.empty:
                        res.append(j.value)
                jobs.clear()
        gevent.joinall(jobs, timeout=30)
        for j in jobs:
            if j.value is not None and not j.value.empty:
                res.append(j.value)
        jobs.clear()
        if len(res) != 0:
            return pd.concat(res)
        return pd.DataFrame()

    def _check_df(self,freq, df, daily_bars):
        if freq == '1m':
            need_check = pd.DataFrame({
                'open': df['open'].resample('1D').first(),
                'high': df['high'].resample('1D').max(),
                'low': df['low'].resample('1D').min(),
                'close': df['close'].resample('1D').last(),
                'volume': df['volume'].resample('1D').sum()
            }).dropna()
        else:
            need_check = df

        daily_bars = daily_bars[daily_bars.index >= need_check.index[0]]

        if daily_bars.shape[0] != need_check.shape[0]:
            logger.warning(
                "{} merged {}, expected {}".format(daily_bars.code[0], need_check.shape[0], daily_bars.shape[0]))
            need_check = fillna(need_check.reindex(daily_bars.index, copy=False))
        diff = daily_bars[['open', 'close']] == need_check[['open', 'close']]
        res = (diff.open) & (diff.close)
        sessions = res[res == False].index
        return sessions

    def get_k_data(self, code, start, end, freq, check=True):
        if isinstance(start, str) or isinstance(end, str):
            start = pd.Timestamp(start)
            end = pd.Timestamp(end)
        if check:
            daily_bars = self.get_security_bars(code, '1d', start, end)
            if daily_bars is None or daily_bars.empty:
                return daily_bars
            sessions = daily_bars.index
        else:
            sessions = pd.bdate_range(start, end, weekmask='Mon Tue Wed Thu Fri')
        df = self._get_k_data(code, freq, sessions)

        if not df.empty:
            if check:
                sessions = self._check_df(freq, df, daily_bars)
                if sessions.shape[0] != 0:
                    logger.info("fixing data for {}-{} with sessions: {}".format(code, freq, sessions))
                    fix = self._get_k_data(code, freq, sessions)
                    df.loc[fix.index] = fix
            return df
        return df


class AsyncEngine(Engine):
    def __init__(self, *args, **kwargs):
        super(AsyncEngine, self).__init__(*args, **kwargs)

        self.aapi = ATdxHq_API(ip=self.ip)

    async def _get_transaction(self, code, date):
        res = []
        start = 0
        while True:
            data = await self.aapi.get_history_transaction_data(get_stock_type(code), code, start, 2000,
                                                                date)
            if not data:
                break
            start += 2000
            res = data + res
            if len(data) < 2000:
                break

        if len(res) == 0:
            return pd.DataFrame()
        df = self.api.to_df(res).assign(date=date)
        df.loc[0, 'time'] = df.time[1]
        df.index = pd.to_datetime(str(date) + " " + df["time"])
        df['code'] = code
        return df.drop("time", axis=1)

    def get_async_security_bars(self, code, freq, start=None, end=None, index=False):
        if not isinstance(code, list):
            code = [code]

        res = [self._get_security_bars1(c, freq, start, end, index) for c in code]
        completed, pending = self.aapi.run_until_complete(asyncio.wait(res))

        return [r.result() for r in completed]

    async def _get_security_bars1(self,c, freq, start, end, index):
        return c, await self._get_security_bars(c, freq, start, end, index)

    @retry(3)
    async def _get_security_bars(self, code, freq, start=None, end=None, index=False):
        if index:
            exchange = self.get_security_type(code)
            func = self.aapi.get_index_bars
        else:
            exchange = get_stock_type(code)
            func = self.aapi.get_security_bars

        if start:
            start = start.tz_localize(None)
        if end:
            end = end.tz_localize(None)

        if freq in ['1d', 'day']:
            freq = 9
        elif freq in ['1m', 'min']:
            freq = 8
        else:
            raise Exception("1d and 1m frequency supported only")

        res = []
        pos = 0
        retry = False
        while True:
            data = await func(freq, exchange, code, pos, 800)
            if data == None:
                print("None data")
                break
            res = data + res
            pos += 800

            if isinstance(data,list) and len(data) < 800:
                break

            try:
                if start and pd.to_datetime(data[0]['datetime']) < start:
                    break
            except:
                print(code, data[0])
        try:
            if len(res) == 0:
                print("no k data for {}".format(code))
                return pd.DataFrame()
            df = self.api.to_df(res).drop(
                ['year', 'month', 'day', 'hour', 'minute'], axis=1)
            try:
                df['datetime'] = pd.to_datetime(df.datetime)
            except: # 服务器返回的k线时间有误，0000-00-00
                mask = df.open == 0
                mask = mask[mask == True]
                startDate, endDate = mask.index[[0,-1]]
                df = df[df.open != 0]
                df['datetime'] = pd.to_datetime(df.datetime)
                logger.warning("symbol {0} meet date error, "
                    "from date {1} to {2} not including {1} and {2}, "
                    "we just skip it!"
                    .format(code,
                    df['datetime'][startDate - 1],
                    df['datetime'][endDate + 1])
                )

            df.set_index('datetime', inplace=True)
            if freq == 9:
                df.index = df.index.normalize()
        except ValueError:  # 未上市股票，无数据
            logger.warning("no k line data for {}".format(code))
            traceback.print_exc()
            return pd.DataFrame()
        close = [df.close.values[-1]]
        if start:
            df = df.loc[lambda df: start <= df.index]
        if end:
            df = df.loc[lambda df: df.index.normalize() <= end]

        if df.empty:
            return pd.DataFrame()
        else:
            df['code'] = code
            return df

    def _get_k_data(self, code, freq, sessions):
        trade_days = map(int, sessions.strftime("%Y%m%d"))
        if freq == '1m':
            freq = '1 min'

        if freq == '1d':
            freq = '24 H'

        res = [self._get_transaction(code, trade_day) for trade_day in
               trade_days]
        completed, pending = self.aapi.run_until_complete(asyncio.wait(res))
        res = [Engine.minute_bars_from_transaction(t.result(), freq=freq) for t in completed]

        if len(res) != 0:
            return pd.concat(res).sort_index()
        return pd.DataFrame()


class ExEngine:
    def __init__(self, *args, **kwargs):
        self.api = TdxExHq_API(args, kwargs)

    def connect(self):
        self.api.connect('61.152.107.141', 7727)
        return self

    def __enter__(self):
        return self

    def exit(self):
        self.api.disconnect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.disconnect()

    @lazyval
    def markets(self):
        return self.api.to_df(self.api.get_markets())


if __name__ == '__main__':
    aeg = AsyncEngine(ip='202.108.253.130', auto_retry=True, raise_exception=True)
    aeg.connect()
    start = pd.Timestamp('1990-12-19')
    end  = pd.Timestamp('2018-02-02')
    df = aeg.get_k_data('000049', start, end, '1m')
    print(df)