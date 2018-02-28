###############################################################################
#
#   Agora Portfolio & Risk Management System
#
#   Copyright 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from onyx.core import Curve, DateRange

import urllib.request
import json
import pickle
import getpass
import os

BASE = "https://openexchangerates.org/api"

USER = getpass.getuser()
APP_ID = os.getenv("OPENEXCHANGERATES_APP_ID",
                   "8a439112054749a080ae72ce3114790c")
CACHE_FOLDER = os.getenv("FX_CACHE", os.path.join("/home", USER, "tmp"))


# -----------------------------------------------------------------------------
def __fetch_hist(date=None, app_id=APP_ID):
    if date is None:
        url = "{0:s}/latest.json?app_id={1:s}".format(BASE, app_id)
    else:
        url = "{0:s}/historical/{1:s}.json?"\
              "app_id={2:s}".format(BASE, date.strftime("%Y-%m-%d"), app_id)

    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))
    del data["disclaimer"]
    del data["license"]
    return data


# -----------------------------------------------------------------------------
def get_rate(date, ccy, cache_folder=None):
    cache_folder = cache_folder or CACHE_FOLDER
    file_name = os.path.join(cache_folder,
                             date.strftime("fx_cache_%Y-%m-%d.dat"))
    try:
        with open(file_name, "rb") as cache_file:
            data = pickle.load(cache_file)

    except FileNotFoundError:
        data = __fetch_hist(date)
        with open(file_name, "wb") as cache_file:
            pickle.dump(data, cache_file, -1)

    return data["rates"][ccy]


# -----------------------------------------------------------------------------
def fetch_historical(ccy, start, end, cache=None):
    """
    Description:
        Return historical prices for the ccy/USD cross, i.e. the value of
        1 unit of currency in US$ (sourced from www.openexchangerates.com).
    Inputs:
        ccy   - the currency crossed agains USD (ccy/USD)
        start - the start date
        end   - the end date
        cache - the folder used to cache files
    Returns:
        A Curve.
    """
    dts, vls = [], []
    for date in DateRange(start, end, "+1d"):
        try:
            value = 1.0 / get_rate(date, ccy, cache)
        except KeyError:
            pass
        else:
            dts.append(date)
            vls.append(value)

    if not len(dts):
        raise RuntimeError("No rates available for {0:s} in the "
                           "range {1!s} - {2!s}.".format(ccy, start, end))

    return Curve(dts, vls)
