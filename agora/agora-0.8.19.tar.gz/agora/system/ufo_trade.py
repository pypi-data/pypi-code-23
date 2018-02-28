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

from onyx.core import(Structure, DateOffset,
                      DelObj, CreateInMemory, ObjDbTransaction,
                      ObjDbQuery, ValueType, GetVal, UfoBase, ReferenceField,
                      IntField, FloatField, DateField, SelectField, BoolField)

from agora.corelibs.tradable_api import AddByInference
from agora.corelibs.transaction_api import TransactionsBy
from agora.system.ufo_transaction import Transaction
from agora.tradables.ufo_forward_cash import ForwardCash
from agora.risk.core_functions import WithRiskValueTypes

import random

__all__ = ["Trade", "TradeError", "TradeWarning"]


TRANSACTIONS_STORED = """
SELECT Event, Transaction
FROM (
    SELECT Event, Transaction
    FROM PosEffects
    WHERE Trade=%s AND Book=%s
) tab1 INNER JOIN LATERAL (
    SELECT FROM Objects
    WHERE Name=Transaction AND Data@>'{"Marker": "HEAD"}'::jsonb
    LIMIT 1
) tab2 ON true;
"""


###############################################################################
class TradeError(Exception):
    pass


###############################################################################
class TradeWarning(Warning):
    pass


###############################################################################
@WithRiskValueTypes
class Trade(UfoBase):
    """
    Class used to represent trade objects in the system and their effects
    on positions.
    """
    SecurityTraded = ReferenceField(obj_type="TradableObj")
    TradeDate = DateField()
    TradeType = SelectField(default="Buy", options=["Buy", "Sell"])
    Quantity = IntField(default=0, positive=True)
    UnitPrice = FloatField(default=0.0, positive=True)
    PaymentUnit = ReferenceField(obj_type="Currency")
    SettlementDate = DateField()
    Party = ReferenceField(obj_type="Book")
    Counterparty = ReferenceField(obj_type="Book")
    Trader = ReferenceField(obj_type="Trader")
    Broker = ReferenceField(obj_type="Broker")
    BrokerageFee = FloatField(default=0.0, positive=True)
    OtherCosts = FloatField(default=0.0, positive=True)
    Deleted = BoolField(default=False)

    # -------------------------------------------------------------------------
    def __post_init__(self):
        # --- set object's name if not set already
        self.Name = self.Name or Trade.random_name()

        # --- set default values
        self.PaymentUnit = self.PaymentUnit or "USD"

        if self.SettlementDate is None:
            cal = GetVal(self.PaymentUnit, "HolidayCalendar")
            self.SettlementDate = DateOffset(self.TradeDate, "+2b", cal)

        self.Broker = self.Broker or "BROKER-SUSPENSE"

    # -------------------------------------------------------------------------
    @ValueType()
    def Denominated(self, graph):
        """
        A trade is denominated in the PaymentUnit currency.
        """
        return graph(self, "PaymentUnit")

    # -------------------------------------------------------------------------
    @ValueType()
    def TradeInfo(self, graph):
        """
        Return a dictionary {attribute: value}, including all the stored
        attributes.
        """
        attrs = sorted(self._json_fields)
        return dict(zip(attrs, [graph(self, attr) for attr in attrs]))

    # -------------------------------------------------------------------------
    @ValueType()
    def TransactionsCalc(self, graph):
        sec = graph(self, "SecurityTraded")
        trd_date = graph(self, "TradeDate")
        trd_type = graph(self, "TradeType")
        trd_qty = graph(self, "Quantity")
        qty = trd_qty*(1.0 if trd_type == "Buy" else -1.0)
        ccy = graph(self, "PaymentUnit")
        prc = graph(self, "UnitPrice")
        sett_dt = graph(self, "SettlementDate")
        cash = ForwardCash(Currency=ccy, PaymentDate=sett_dt)
        cash = AddByInference(cash, in_memory=True)

        return {
            "BuySell": CreateInMemory(Transaction(
                TransactionDate=trd_date,
                SecurityTraded=sec,
                Quantity=qty,
                Party=graph(self, "Party"),
                Counterparty=graph(self, "Counterparty"),
                Event="BuySell",
                Trade=self.Name
            )),
            "Payment": CreateInMemory(Transaction(
                TransactionDate=trd_date,
                SecurityTraded=cash.Name,
                Quantity=-qty*prc,
                Party=graph(self, "Party"),
                Counterparty=graph(self, "Counterparty"),
                Event="Payment",
                Trade=self.Name
            )),
            "Costs": CreateInMemory(Transaction(
                TransactionDate=trd_date,
                SecurityTraded=cash.Name,
                Quantity=-graph(self, "OtherCosts"),
                Party=graph(self, "Party"),
                Counterparty="TAXNCOSTS",
                Event="Costs",
                Trade=self.Name
            )),
            "Fees": CreateInMemory(Transaction(
                TransactionDate=trd_date,
                SecurityTraded=cash.Name,
                Quantity=-graph(self, "BrokerageFee"),
                Party=graph(self, "Party"),
                Counterparty=graph(self, "Broker"),
                Event="Fees",
                Trade=self.Name
            ))
        }

    # -------------------------------------------------------------------------
    @ValueType()
    def Leaves(self, graph):
        leaves = Structure()
        for transaction in graph(self, "TransactionsCalc").values():
            leaves += graph(transaction, "Leaves")
        return leaves

    # -------------------------------------------------------------------------
    @ValueType()
    def MktValUSD(self, graph):
        mtm = 0.0
        for leaf, qty in graph(self, "Leaves").items():
            mtm += qty*graph(leaf, "MktValUSD")
        return mtm

    # -------------------------------------------------------------------------
    @ValueType()
    def MktVal(self, graph):
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    @ValueType()
    def PositionEffects(self, graph):
        pos_effects = []
        for transaction in self.transactions_stored().values():
            pos_effects += graph(transaction, "PositionEffects")
        return pos_effects

    # -------------------------------------------------------------------------
    @ValueType()
    def PositionEffectsCalc(self, graph):
        pos_effects = []
        for transaction in graph(self, "TransactionsCalc").values():
            pos_effects += graph(transaction, "PositionEffects")
        return pos_effects

    # -------------------------------------------------------------------------
    def delete(self):
        if GetVal("Database", "TradesDeletable"):
            transactions = TransactionsBy(trade=self.Name, head_only=False)
            with ObjDbTransaction("Delete Children", "SERIALIZABLE"):
                for transaction in transactions:
                    DelObj(transaction)
        else:
            raise TradeError("Trying to delete a trade without permission")

    # -------------------------------------------------------------------------
    # NB: this needs to be a standard method to make sure that there is never
    #     any caching on trade.Name and trade.Party (for clarity sake we
    #     refrain from making this a property).
    def transactions_stored(self):
        rows = ObjDbQuery(TRANSACTIONS_STORED,
                          (self.Name, self.Party), attr="fetchall")

        stored = {}
        for row in rows:
            try:
                stored[row.event].append(row.transaction)
            except AttributeError:
                stored[row.event] = [stored[row.event], row.transaction]
            except KeyError:
                stored[row.event] = row.transaction

        return stored

    # -------------------------------------------------------------------------
    @classmethod
    def random_name(cls):
        return "TmpTrd-{0:>07d}".format(random.randrange(0, 10000000, 1))

    # -------------------------------------------------------------------------
    @classmethod
    def format_name(cls, date, trd_id):
        return "TRD {0:s} {1:s}".format(date.strftime("%Y%m%d"), trd_id)


# -----------------------------------------------------------------------------
def prepare_for_test():
    from onyx.core import Date, AddIfMissing

    import agora.system.ufo_book as ufo_book
    import agora.system.ufo_trader as ufo_trader
    import agora.system.ufo_broker as ufo_broker
    import agora.tradables.ufo_equity_cash as ufo_equity_cash
    import agora.tradables.ufo_equity_cfd as ufo_equity_cfd
    import agora.tradables.ufo_forward_cash as ufo_forward_cash

    books = ufo_book.prepare_for_test()
    traders = ufo_trader.prepare_for_test()
    brokers = ufo_broker.prepare_for_test()
    eqcash = ufo_equity_cash.prepare_for_test()
    eqcfds = ufo_equity_cfd.prepare_for_test()

    ufo_forward_cash.prepare_for_test()

    trades = [
        # --- this is a cash trade
        {
            "SecurityTraded": eqcash[0],
            "TradeDate": Date.today(),
            "TradeType": "Sell",
            "Quantity": 1000,
            "Party": books[0],
            "Counterparty": books[2],
            "Trader": traders[0],
            "Broker": brokers[0],
            "UnitPrice": 9.1*1.5/1.15,
            "PaymentUnit": "EUR",
        },
        # --- this is a CFD trade
        {
            "SecurityTraded": eqcfds[0],
            "TradeDate": Date.today(),
            "TradeType": "Sell",
            "Quantity": 1000,
            "Party": books[0],
            "Counterparty": books[2],
            "Trader": traders[0],
            "Broker": brokers[0],
        }
    ]
    trades = [AddIfMissing(Trade(**trade_info)) for trade_info in trades]

    return [trade.Name for trade in trades]
