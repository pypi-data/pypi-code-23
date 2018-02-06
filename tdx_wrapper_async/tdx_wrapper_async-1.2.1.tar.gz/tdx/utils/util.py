from decimal import Decimal, ROUND_HALF_UP
import pandas as pd


def precise_round(num):
    return float(Decimal(str(num)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def fillna(df):
    mask = pd.isnull(df.open)
    df.close.fillna(method='pad', inplace=True)
    df.volume.fillna(0, inplace=True)
    df.loc[mask, ["high", "low", "open"]] = df.loc[mask, "close"]
    return df


def select_best_ip():
    # '115.238.90.165', 60.191.117.167, 218.75.126.9, 124.160.88.183, '60.12.136.250'
    # '218.108.98.244','218.108.47.69'
    # 去除一些timeout 和 返回错误数据的ip
    listx = ['180.153.18.170', '180.153.18.171', '202.108.253.130', '202.108.253.131',
             '180.153.39.51']
    data = [ping(x) for x in listx]
    return listx[data.index(min(data))]