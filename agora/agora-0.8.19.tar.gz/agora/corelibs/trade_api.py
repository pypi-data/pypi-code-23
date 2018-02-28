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

from onyx.core import (unique_id, Date, Structure,
                       AddObj, GetObj, UpdateObj, PurgeObj,
                       ObjDbTransaction, CreateInMemory, ObjDbQuery,
                       ObjNotFound, GetVal, SetVal)

from agora.corelibs.tradable_api import AddByInference
from agora.corelibs.transaction_api import CommitTransaction, DeleteTransaction
from agora.system.ufo_transaction import TransactionWarning
from agora.system.ufo_trade import TradeError, TradeWarning

import logging

__all__ = [
    "TradeError",
    "CommitTrade",
    "DeleteTrade",
    "ChildrenByBook",
    "TradesBy",
]

LOG_FMT = "%(asctime)-15s %(levelname)-8s %(name)-38s %(message)s"

logging.basicConfig(level=logging.INFO, format=LOG_FMT)
logger = logging.getLogger(__name__)

# --- templates for common queries
QUERY_KIDSBYBOOK = """
SELECT Unit, SUM(Qty) AS tot_qty
FROM PosEffects WHERE Book=%s AND {0:s}<=%s
GROUP BY Unit;"""


# -----------------------------------------------------------------------------
def PreTradeCompliance(trade):
    """
    Description:
        This function is ment to raise an exception for any violation
        of pre-trade compliance checks.
    Inpots:
        trade - the trade to be checked
    Returns:
        None.
    """
    # --- price validation
    GetVal(trade, "MktValUSD")

    # --- basic risk validation
    GetVal(trade, "Deltas")


# -------------------------------------------------------------------------
def CommitTrade(trade, name=None):
    """
    Description:
        Create/amend a trade by creting/amending the associated transactions.
    Inputs:
        trade - the instance of Trade to commit
        name  - an optional trade name
    Returns:
        A Trade instance.
    """
    # --- clone security traded: AddByInference is needed to generate the
    #     proper ImpliedName.
    sec = AddByInference(GetObj(trade.SecurityTraded).clone())

    # --- get trade info before reloading the trade
    info = GetVal(trade, "TradeInfo")
    info["SecurityTraded"] = sec.Name

    try:
        # --- reload security: this is needed to avoid basing decisions on
        #     attribute values that might have been set in memory
        trade = GetObj(trade.Name, refresh=True)

    except ObjNotFound:
        # --- trade not found, proceed as new trade
        trade.SecurityTraded = sec.Name

        # --- create trade and overwrite a few stored attributes
        name = name or trade.format_name(Date.today(), unique_id(8))
        trade = CreateInMemory(trade.clone(Name=name))

        PreTradeCompliance(trade)

        logger.info("creating new trade {0:s}".format(trade.Name))

        calculated = GetVal(trade, "TransactionsCalc")
        with ObjDbTransaction("Trade Insert", level="SERIALIZABLE"):
            for transaction in calculated.values():
                CommitTransaction(transaction)
            AddObj(trade)

    else:
        # --- need to amend?
        same = True
        for attr, value in info.items():
            same = (value == getattr(trade, attr))
            if not same:
                break
        if same:
            raise TradeWarning("{0:s}, TradeCommit found nothing to "
                               "amend on existing trade.".format(trade.Name))

        logger.info("amending trade {0:s}".format(trade.Name))

        # --- we fetch stored transactions before overwriting the stored
        #     attributes of the trade (this is essential since amending the
        #     Party attribute would prevent fetching the correct stored
        #     transactions).
        stored = trade.transactions_stored()  # this queries the backend

        if not len(stored):
            raise TradeError("{0:s}, error loading "
                             "transactions stored.".format(trade.Name))

        # --- overwrite trade stored attributes with new ones
        for attr, value in info.items():
            SetVal(trade, attr, value)

        PreTradeCompliance(trade)

        calculated = GetVal(trade, "TransactionsCalc")
        with ObjDbTransaction("Trade Amend", level="SERIALIZABLE"):
            UpdateObj(trade.Name)
            for event, transaction in calculated.items():
                # --- overwrite the name of the calculated transaction with
                #     that of the stored one
                try:
                    stored_name = stored[event]
                except KeyError:
                    raise TradeError("{0:s}, trying to amend a trade with "
                                     "an aged transaction.".format(trade.Name))
                try:
                    CommitTransaction(transaction, stored_name)
                except TransactionWarning as warning:
                    # --- ignore warnings
                    logger.info(warning)

    return trade


# -------------------------------------------------------------------------
def DeleteTrade(trade_name):
    """
    Description:
        Delete a trade, by deleting all associated transactions and marking it
        as deleted.
    Inputs:
        trade_name - the name of the trade to delete
    Returns:
        None.
    """
    # --- reload security: this is needed to avoid basing decisions on
    #     attribute values that might have been set in memory
    trade = GetObj(trade_name, refresh=True)

    with ObjDbTransaction("Trade Delete", level="SERIALIZABLE"):
        if trade.TimeCreated >= Date.today():
            # --- same day delete: get rid of the trade and of all associated
            #     transactions
            PurgeObj(trade)
        else:
            trade.Deleted = True
            UpdateObj(trade)
            for transaction in trade.transactions_stored().values():
                if isinstance(transaction, list):
                    for sub_transaction in transaction:
                        DeleteTransaction(sub_transaction)
                else:
                    DeleteTransaction(transaction)


# -----------------------------------------------------------------------------
def ChildrenByBook(book, pos_date, by_time_created=False):
    """
    Description:
        Return all children of a given book as of a given date.
    Inputs:
        book            - the book
        pos_date        - the positions date
        by_time_created - if True, amendments are reflected on the date they
                          were booked, not on the date of the original trade.
    Returns:
        A Structure.
    """
    if by_time_created:
        query = QUERY_KIDSBYBOOK.format("TimeCreated")
    else:
        query = QUERY_KIDSBYBOOK.format("TradeDate")

    rows = ObjDbQuery(query, parms=(book, pos_date.eod()), attr="fetchall")
    children = Structure()
    for row in rows:
        # --- exclude children with zero quantity
        if row.tot_qty != 0.0:
            children[row.unit] = row.tot_qty

    return children


# -----------------------------------------------------------------------------
def TradesBy(book=None, trader=None,
             security=None, sectype=None, date_range=None):
    """
    Description:
        Return all trades matching the given criteria.
    Inputs:
        book       - a given book
        trader     - a given trader
        security   - a given security
        sectype    - a given security type
        date_range - a tuple of start and end date
    Returns:
        A list of trade names.
    """
    extquery = []
    criteria = []

    if book is not None:
        extquery.append("Book=%s")
        criteria.append(book)

    if security is not None:
        extquery.append("Unit=%s")
        criteria.append(security)

    if sectype is not None:
        extquery.append("UnitType=%s")
        criteria.append(sectype)

    if date_range is not None:
        extquery.append("TradeDate BETWEEN %s AND %s")
        criteria.append(date_range[0])
        criteria.append(date_range[1])

    if len(criteria):
        query = ("SELECT DISTINCT(Trade) "
                 "FROM PosEffects WHERE {0:s};").format(" AND ".join(extquery))
        rows = ObjDbQuery(query, parms=criteria, attr="fetchall")

    else:
        query = "SELECT DISTINCT(Trade) FROM PosEffects;"
        rows = ObjDbQuery(query, attr="fetchall")

    # --- postprocessing filters
    if trader is not None:
        # --- Trader is not part of PosEffects table: run filter as a
        #     post-process
        def post_proc(trade_name):
            trade = GetObj(trade_name)
            return trade.Trader == trader and not trade.Deleted
    else:
        def post_proc(trade_name):
            trade = GetObj(trade_name)
            return not trade.Deleted

    return [row.trade for row in rows if post_proc(row.trade)]
