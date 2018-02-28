###############################################################################
#
#   Agora Portfolio & Risk Management System
#
#   Copyright © 2015 Carlo Sbraccia
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

from onyx.core import (GCurve, Interpolate, RDate, DateRange, Structure,
                       GetObj, AddObj, UpdateObj, ExistsInDatabase,
                       ObjDbTransaction, ObjNotFound, ObjDbQuery,
                       EvalBlock, GraphScope, GetVal, SetVal)

from agora.system.ufo_portfolio import Portfolio

__all__ = [
    "get_historical",
    "pnl_by_long_short",
    "update_attribution_hierarchy",
    "stats_by_portfolio",
    "stats_by_container",
]

# --- query to get all assets traded in a given book, skipping all trades that
#     have been subsequently deleted or moved to a different book
ASSETS_BY_BOOK = """
SELECT DISTINCT(Objects.Data->>'Asset') AS Asset FROM (
    SELECT DISTINCT(Objects.Data->>'SecurityTraded') AS SecTraded FROM (
        SELECT Trade As TradeName FROM (
            SELECT Trade, SUM(Qty) AS TotQty
            FROM PosEffects WHERE Book=%s AND UnitType<>'ForwardCash'
            GROUP BY Trade)
        AS Pivot WHERE Pivot.TotQty<>0) AS Trades
    INNER JOIN Objects ON Objects.Name=Trades.TradeName) AS Tradables
INNER JOIN Objects ON Objects.Name=Tradables.SecTraded AND
                      Objects.Data->>'Asset'<>'';
"""

# --- mapping risk metric to value type
RISK_METRIC_TO_VT = {
    "mktval": "MktValUSD",
    "gross": "GrossExposure",
    "net": "NetExposure",
    "fvol": "ForwardVol",
    "var": "AdjVaR",
    "aum": "Aum",
    "nav": "Nav",
}

# -----------------------------------------------------------------------------
def get_historical(port, start, end, fields, fund=None, overrides=None):
    """
    Description:
        Get historical values for a given portfolio.
    Inputs:
        port      - portfolio name
        start     - start date
        end       - end date
        fields    - a list of fields.
                    Valid fields are: mktval, gross, net, fvol, var, aum, nav
        fund      - this field is required to retrieve aum and/or nav
        overrides - a dictionary that specifies how to map fields to value types
    Returns:
        A GCurve of dictionaries with field values.
    """
    fields = dict.fromkeys(fields, True)
    overrides = overrides or {}

    add_mktval = fields.pop("mktval", False)
    add_gross = fields.pop("gross", False)
    add_net = fields.pop("net", False)
    add_fvol = fields.pop("fvol", False)
    add_var = fields.pop("var", False)
    add_aum = fields.pop("aum", False)
    add_nav = fields.pop("nav", False)

    mapping = RISK_METRIC_TO_VT.copy()
    mapping.update(overrides)

    if len(fields):
        raise ValueError("Unrecognized fields: {0!s}".format(fields))

    results = GCurve()
    for date in DateRange(start, end, "+1b"):
        values = {}
        with EvalBlock() as eb:
            # --- this shifts back both market and positions
            eb.change_value("Database", "PricingDate", date)
            if add_mktval:
                values["mktval"] = GetVal(port, mapping["mktval"])
            if add_gross:
                values["gross"] = GetVal(port, mapping["gross"])
            if add_net:
                values["net"] = GetVal(port, mapping["net"])
            if add_fvol:
                values["fvol"] = GetVal(port, mapping["fvol"])
            if add_var:
                values["var"] = GetVal(port, mapping["var"])
            if add_aum and fund is not None:
                values["aum"] = GetVal(fund, mapping["aum"])
            if add_nav and fund is not None:
                values["nav"] = GetVal(fund, mapping["nav"])

        results[date] = values

    return results


# -----------------------------------------------------------------------------
def pnl_by_long_short(port, start, end):
    """
    Description:
        Return historical daily P&L for long and short positions of a given
        portfolio, using the delta approximation.
        NB: We use adjusted prices to include the effect of dividends and
            assume that all positions are finaced in local currency (so that
            there is FX risk on the daily P&L only).
    Inputs:
        port  - portfolio name
        start - start date
        end   - end date
    Returns:
        A GCurve of dictionaries with field values.
    """
    crv_start = start + RDate("-1w")

    def get_price(sec, date):
        crv = GetVal(sec, "GetCurve", start=crv_start, end=end, field="Close")
        mul = GetVal(sec, "Multiplier")
        return mul*Interpolate(crv, date)

    def get_fx_rate(sec, date):
        cross = "{0:3s}/USD".format(GetVal(sec, "Denominated"))
        crv = GetVal(cross, "GetCurve", start=crv_start, end=end)
        return Interpolate(crv, date)

    def get_pos_and_prices(port, date):
        with EvalBlock() as eb:
            eb.change_value("Database", "PricingDate", date)
            pos = GetVal(port, "Deltas")
        return pos, {sec: get_price(sec, date) for sec in pos}

    date = start + RDate("-1b")
    old_pos, old_prcs = get_pos_and_prices(port, date)
    results = GCurve()

    for date in DateRange(start, end, "+1b"):
        fx_rates = {sec: get_fx_rate(sec, date) for sec in old_pos}
        long = short = 0.0
        for sec, qty in old_pos.items():
            pnl = qty*(get_price(sec, date) - old_prcs[sec])*fx_rates[sec]
            if qty >= 0.0:
                long += pnl
            else:
                short += pnl

        results[date] = {"long": long, "short": short}

        old_pos, old_prcs = get_pos_and_prices(port, date)

    return results


# -----------------------------------------------------------------------------
def update_attribution_hierarchy(fund):
    """
    Description:
        Updates the equity attribution hierarchy for all books that are leaves
        of a given fund.
    Inputs:
        fund - the fund's name
    Returns:
        None
    """
    port = GetVal(fund, "Portfolio")
    books = GetVal(port, "Books")
    fund_ccy = GetVal(fund, "Denominated")

    with ObjDbTransaction("Rebuild hierarchy"):
        # --- first wipe clean all attribution portfolios
        for container in ("Countries", "Regions", "Sectors", "Subsectors"):
            for bucket in GetVal(container, "Items"):
                name = "{0:s} {1:s}".format(port, bucket.upper())
                try:
                    SetVal(name, "Children", Structure())
                except ObjNotFound:
                    continue

        # --- then add each book in the hierarchy to the relevant attribution
        #     portfolios
        for book in books:
            # --- lookup the set of all assets traded in this book
            assets = {rec.asset for rec in
                      ObjDbQuery(ASSETS_BY_BOOK, (book, ), attr="fetchall")}

            if not len(assets):
                continue

            for attr in ("Country", "Region", "Sector", "Subsector"):
                buckets = {GetVal(asset, attr) for asset in assets}
                qty = 1.0 / float(len(buckets))

                for bucket_name in buckets:
                    name = "{0:s} {1:s}".format(port, bucket_name.upper())
                    try:
                        bucket = GetObj(name)
                    except ObjNotFound:
                        bucket = AddObj(Portfolio(Name=name,
                                                  DisplayName=bucket_name,
                                                  Denominated=fund_ccy))
                    children = bucket.Children or Structure()
                    children[book] = qty
                    bucket.Children = children
                    UpdateObj(bucket)


# -----------------------------------------------------------------------------
def stats_by_portfolio(fund, month):
    """
    Description:
        Return attribution statistics (Gross Exposure, Net Exposure, and MTD
        P&L) on a given month for all the children of a given fund.
    Inputs:
        fund  - the fund's name
        month - the month's date (usually the last day)
    Returns:
        A dictionary.
    """
    port = GetVal(fund, "Portfolio")
    start = month + RDate("-1m+e")
    end = month + RDate("+e")
    stats = {}

    scope_start = GraphScope()
    scope_start.change_value("Database", "PricingDate", start)
    scope_end = GraphScope()
    scope_end.change_value("Database", "PricingDate", end)

    with scope_end:
        stats = {
            "date": end,
            "aum": GetVal(fund, "Aum"),
            "nav": GetVal(fund, "Nav"),
        }

    for kid in GetVal(port, "Children"):
        with scope_start:
            mktval_start = GetVal(kid, "MktValUSD")
        with scope_end:
            info = {
                "gross": GetVal(kid, "GrossExposure"),
                "net": GetVal(kid, "NetExposure"),
                "mtd pnl": GetVal(kid, "MktValUSD") - mktval_start,
            }
        stats[GetVal(kid, "DisplayName")] = info

    return stats


# -----------------------------------------------------------------------------
def stats_by_container(container, fund, month):
    """
    Description:
        Return attribution statistics (Gross Exposure, Net Exposure, and MTD
        P&L) on a given month for all the portfolios in a given container.
    Inputs:
        container - the container's name
        fund      - the fund's name (used to get AUM)
        month     - the month's date (usually the last day, but it doesn't
                    really matter)
    Returns:
        A dictionary.
    """
    port = GetVal(fund, "Portfolio")
    start = month + RDate("-1m+e")
    end = month + RDate("+e")
    stats = {}

    scope_start = GraphScope()
    scope_start.change_value("Database", "PricingDate", start)
    scope_end = GraphScope()
    scope_end.change_value("Database", "PricingDate", end)

    with scope_end:
        stats = {
            "date": end,
            "aum": GetVal(fund, "Aum"),
            "nav": GetVal(fund, "Nav"),
        }

    for item in GetVal(container, "Items"):
        kid = "{0:s} {1:s}".format(port, item.upper())
        if not ExistsInDatabase(kid):
            continue
        with scope_start:
            mktval_start = GetVal(kid, "MktValUSD")
        with scope_end:
            info = {
                "gross": GetVal(kid, "GrossExposure"),
                "net": GetVal(kid, "NetExposure"),
                "mtd pnl": GetVal(kid, "MktValUSD") - mktval_start,
            }
        stats[GetVal(kid, "DisplayName")] = info

    return stats
