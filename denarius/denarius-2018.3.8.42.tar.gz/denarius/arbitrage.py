# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# arbitrage                                                                    #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program provides arbitrage utilities.                                   #
#                                                                              #
# copyright (C) 2018 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################
"""

from __future__ import division
import datetime
import json
import logging
import os
import random
import requests
import time

from bs4 import BeautifulSoup
import currency_converter
import pandas as pd
import pyprel
import technicolor

__name__    = "arbitrage"
__version__ = "2018-03-08T0042Z"

log = logging.getLogger(__name__)
log.addHandler(technicolor.ColorisingStreamHandler())
log.setLevel(logging.INFO)

def DataFrame_LBC_UK_buy_ads():
    """
    Return a DataFrame of current LocalBitcoins UK buy ads.
    """
    log.info("get LocalBitcoins UK buy ads DataFrame")
    timestamp = datetime.datetime.utcnow()
    LBC_UK_buy_ads = [ad for ad in requests.get("https://localbitcoins.com/buy-bitcoins-online/GB/united-kingdom/national-bank-transfer/.json").json()["data"]["ad_list"]]
    df = pd.DataFrame(columns = ["datetime", "temp_price_gbp", "seller_index", "seller_username", "seller_feedback_score", "seller_trade_count"])
    for index, ad in enumerate(LBC_UK_buy_ads):
        df = df.append(
            {
                "datetime"                     : timestamp,
                "seller_index"                 : index,
                "temp_price_gbp"               : float(ad["data"]["temp_price"]),
                "seller_username"              :       ad["data"]["profile"]["username"],
                "seller_feedback_score"        : float(ad["data"]["profile"]["feedback_score"]),
                "seller_trade_count"           :       ad["data"]["profile"]["trade_count"],
                "max_amount"                   :       ad["data"]["max_amount"],
                "min_amount"                   :       ad["data"]["min_amount"],
                "ad_id"                        :       ad["data"]["ad_id"],
                "bank_name"                    :       ad["data"]["bank_name"],
                "online_provider"              :       ad["data"]["online_provider"],
                "payment_window_minutes"       : float(ad["data"]["payment_window_minutes"]),
                "require_feedback_score"       : float(ad["data"]["require_feedback_score"]),
                "require_identification"       :       ad["data"]["require_identification"],
                "require_trade_volume"         : float(ad["data"]["require_trade_volume"]),
                "require_trusted_by_advertiser":       ad["data"]["require_trusted_by_advertiser"],
                "sms_verification_required"    :       ad["data"]["sms_verification_required"],
                "trade_type"                   :       ad["data"]["trade_type"],
                "trusted_required"             :       ad["data"]["trusted_required"],
                "volume_coefficient_btc"       : float(ad["data"]["volume_coefficient_btc"])
            },
            ignore_index = True
        )
    return df

def DataFrame_Kraken_ticker_BTC_EUR():
    """
    Return a DataFrame of current and recent Kraken Bitcoin prices expressed in Euros.
    """
    log.info("get Kraken ticker DataFrame")
    Kraken_ticker = requests.get("https://api.kraken.com/0/public/Ticker?pair=XBTEUR").json()["result"]["XXBTZEUR"]
    df = pd.DataFrame(columns = ["datetime", "last_trade_closed_price", "last_trade_closed_price_lot_volume"])
    df = df.append(
        {
            "datetime"                                   : datetime.datetime.utcnow(),
            "ask_price"                                  : float(Kraken_ticker["a"][0]),
            "ask_lot_volume"                             : float(Kraken_ticker["a"][2]),
            "bid_price"                                  : float(Kraken_ticker["b"][0]),
            "bid_lot_volume"                             : float(Kraken_ticker["b"][2]),
            "last_trade_closed_price"                    : float(Kraken_ticker["l"][0]),
            "last_trade_closed_price_lot_volume"         : float(Kraken_ticker["l"][1]),
            "volume_today"                               : float(Kraken_ticker["v"][0]),
            "volume_last_24_hours"                       : float(Kraken_ticker["v"][1]),
            "volume_weighted_average_price_today"        : float(Kraken_ticker["p"][0]),
            "volume_weighted_average_price_last_24_hours": float(Kraken_ticker["p"][1]),
            "number_of_trades_today"                     : float(Kraken_ticker["t"][0]),
            "number_of_trades_last_24_hours"             : float(Kraken_ticker["t"][1]),
            "low_price_today"                            : float(Kraken_ticker["l"][0]),
            "low_price_last_24_hours"                    : float(Kraken_ticker["l"][1]),
            "high_price_today"                           : float(Kraken_ticker["h"][0]),
            "high_price_last_24_hours"                   : float(Kraken_ticker["h"][1]),
            "open_price"                                 : float(Kraken_ticker["o"]),
        },
        ignore_index = True
    )
    return df

def DataFrame_last_recorded_LBC_UK_buy_ads_with_arbitrage_factors(
    filepath_LBC_UK = "LBC_UK.csv",
    filepath_Kraken = "Kraken.csv"
    ):
    if not exist_filepaths(filepaths = [filepath_LBC_UK, filepath_Kraken]):
        return False
    last_price_Kraken_GBP = last_price_Kraken_recorded(filepath_Kraken = filepath_Kraken, currency_output = "GBP")
    df = pd.read_csv(filepath_LBC_UK)
    # get all ads from last timestamp
    df = df.loc[df["datetime"] == df["datetime"].values[-1]]
    df["arbitrage_factor"] = df["temp_price_gbp"] / last_price_Kraken_GBP
    return df

def append_DataFrame_to_CSV(
    df       = None,
    filepath = None
    ):
    log.info("append DataFrame to {filepath}".format(filepath = filepath))
    df.to_csv(filepath, header = not os.path.isfile(filepath), index = False, mode = "a")

def append_arbitrage_DataFrames_to_CSV(
    filepath_LBC_UK = "LBC_UK.csv",
    filepath_Kraken = "Kraken.csv"
    ):
    append_DataFrame_to_CSV(df = DataFrame_LBC_UK_buy_ads(),        filepath = filepath_LBC_UK)
    append_DataFrame_to_CSV(df = DataFrame_Kraken_ticker_BTC_EUR(), filepath = filepath_Kraken)

def loop_append_arbitrage_DataFrames_to_CSV(
    filepath_LBC_UK = "LBC_UK.csv",
    filepath_Kraken = "Kraken.csv",
    interval        = 120
    ):
    while True:
        append_DataFrame_to_CSV(df = DataFrame_LBC_UK_buy_ads(),        filepath = filepath_LBC_UK)
        append_DataFrame_to_CSV(df = DataFrame_Kraken_ticker_BTC_EUR(), filepath = filepath_Kraken)
        log.info("loop in {interval} s".format(interval = interval))
        time.sleep(interval)

def age_timedelta_last_entry_DataFrame_CSV(
    filepath = None
    ):
    if not filepath:
        return False
    df = pd.read_csv(filepath)
    return datetime.datetime.utcnow() - pd.to_datetime(df["datetime"].values[-1]).to_pydatetime()

def arbitrage_factor_required(
    volume_EUR   = 9000,
    net_gain_EUR = 100
    ):
    """
    Return the arbitrage factor required in order to make a specified net gain
    through the changing of a specified volume.

    Kraken EUR to BTC fee:       1.6 %
    Kraken BTC withdraw fee:     0.0005 BTC (~4.36 EUR 2018-03-06T1851Z)
    LBC sell fee:                1 %
    TransferWise GBP to EUR fee: 0.35 % + 0.8 GBP (~0.90 EUR 2018-03-06T1851Z)
    """
    return (net_gain_EUR + 4.36 + 0.90) / volume_EUR + 1 + 0.016 + 0.01 + 0.0035

def last_price_Kraken_recorded(
    filepath_Kraken = "Kraken.csv",
    currency_output = "EUR"
    ):
    if not exist_filepaths(filepaths = [filepath_Kraken]):
        return False
    df_Kraken             = pd.read_csv(filepath_Kraken)
    last_price_Kraken_EUR = float(df_Kraken["last_trade_closed_price"].values[-1])
    if currency_output == "EUR":
        return last_price_Kraken_EUR
    else:
        return convert_currency(currency_input = "EUR", currency_output = currency_output, amount = last_price_Kraken_EUR)

def price_recommendation(
    arbitrage_factor      = None,
    price_lower_limit_GBP = 7000,
    filepath_LBC_UK       = "LBC_UK.csv",
    filepath_Kraken       = "Kraken.csv",
    behaviour             = "maths"
    ):
    """
    Return a price recommendation based on the specified behaviour and a price
    lower limit, if specified.
    """
    if not exist_filepaths(filepaths = [filepath_LBC_UK, filepath_Kraken]):
        return False
    if not arbitrage_factor:
        arbitrage_factor = arbitrage_factor_required()
    if not price_lower_limit_GBP:
        price_lower_limit_GBP = 0
    if behaviour == "calcium":
        """
        From the required arbitrage factor, calculate the price required using
        the last recorded Kraken price. Then, using the last recorded LBC UK
        data, select the next price higher on LBC UK than the minimum price
        required. From this, subtract a pseudorandom number between 0 and
        0.5 GBP.
        """
        last_price_Kraken_GBP = last_price_Kraken_recorded(filepath_Kraken = filepath_Kraken, currency_output = "GBP")
        price_required_GBP    = arbitrage_factor * last_price_Kraken_GBP
        df_LBC_UK             = pd.read_csv(filepath_LBC_UK)
        # get all ads from last timestamp
        df = df_LBC_UK.loc[df_LBC_UK["datetime"] == df_LBC_UK["datetime"].values[-1]]
        # get the first price greater than the price derived from the required arbitrage factor
        next_highest_price_GBP = df.loc[df["temp_price_gbp"] >= price_required_GBP]["temp_price_gbp"].values[0]
        return max(next_highest_price_GBP, price_lower_limit_GBP) - round(random.uniform(0, 0.5), 2)
    elif behaviour == "maths":
        """
        From the required arbitrage factor, calculate the price required using
        the last recorded Kraken price. Then, using the last recorded LBC UK
        data, select the higher of the calculated price and the fourth lowest
        LBC UK price. From this, subtract a pseudorandom number between 0 and
        0.5 GBP.
        """
        last_price_Kraken_GBP = last_price_Kraken_recorded(filepath_Kraken = filepath_Kraken, currency_output = "GBP")
        price_required_GBP    = arbitrage_factor * last_price_Kraken_GBP
        df_LBC_UK             = pd.read_csv(filepath_LBC_UK)
        # get all ads from last timestamp
        df = df_LBC_UK.loc[df_LBC_UK["datetime"] == df_LBC_UK["datetime"].values[-1]]
        return max(price_required_GBP, float(df["temp_price_gbp"].values[3])) - round(random.uniform(0, 0.5), 2)
    else:
        return False

def DataFrame_display_arbitrage():
    df = DataFrame_last_recorded_LBC_UK_buy_ads_with_arbitrage_factors()
    timestamp = df["datetime"].values[-1]
    del df["datetime"]
    del df["ad_id"]
    del df["bank_name"]
    del df["online_provider"]
    del df["payment_window_minutes"]
    del df["require_feedback_score"]
    del df["require_identification"]
    del df["require_trade_volume"]
    del df["require_trusted_by_advertiser"]
    del df["sms_verification_required"]
    del df["trade_type"]
    del df["trusted_required"]
    del df["volume_coefficient_btc"]
    return df

def display_arbitrage():
    df = DataFrame_display_arbitrage()
    log.info(df["datetime"].values[-1])
    log.info(pyprel.Table(contents = pyprel.table_DataFrame(df)))

def arbitrage_ok(
    filepath_LBC_UK = "LBC_UK.csv",
    filepath_Kraken = "Kraken.csv"
    ):
    """
    Check recorded arbitrage data for currency. If the data is not current (of
    age less than 5 minutes), return False.
    """
    if not exist_filepaths(filepaths = [filepath_LBC_UK, filepath_Kraken]):
        return False
    filepaths = [filepath_LBC_UK, filepath_Kraken]
    status = {}
    for filepath in filepaths:
        status[filepath] = age_timedelta_last_entry_DataFrame_CSV(filepath = filepath)
    filepaths_old = [k for k, v in list(status.items()) if v > datetime.timedelta(minutes = 5)]
    for filepath in filepaths_old:
        log.info("{filepath} not updated recently".format(filepath = filepath))
    if filepaths_old:
        return False
    else:
        return True

def exist_filepaths(
    filepaths = None
    ):
    if not filepaths:
        log.error("no filepaths specified")
        return False
    status = {}
    for filepath in filepaths:
        status[filepath] = os.path.isfile(filepath)
    filepaths_nonexistent = [k for k, v in list(status.items()) if not v]
    for filepath in filepaths_nonexistent:
        log.info("{filepath} not found".format(filepath = filepath))
    if filepaths_nonexistent:
        return False
    else:
        return True

def convert_currency(
    currency_input  = None,
    currency_output = None,
    amount          = 1
    ):
    try:
        r = requests.get("https://finance.google.com/finance/converter?a={amount}&from={currency_input}&to={currency_output}".format(
            amount          = amount,
            currency_input  = currency_input,
            currency_output = currency_output
        ))
        soup = BeautifulSoup(r.content, "lxml")
        return float(soup.findAll("span", {"class": "bld"})[0].text.strip(currency_output).strip())
    except:
        log.warning("Google Finance inaccessible for currency conversion, switching to CurrencyConverter")
        try:
            return currency_converter.CurrencyConverter().convert(amount, currency_input, currency_output)
        except:
            return False
