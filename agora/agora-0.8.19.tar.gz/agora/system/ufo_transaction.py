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

from onyx.core import(ObjDbQuery, ValueType, GetVal, UfoBase,
                      DateField, ReferenceField, FloatField, StringField,
                      SelectField)

import collections
import random

__all__ = [
    "Transaction",
    "TransactionError",
    "TransactionWarning"
]


###############################################################################
class TransactionError(Exception):
    pass


###############################################################################
class TransactionWarning(Warning):
    pass


###############################################################################
Position = collections.namedtuple("Position",
                                  "TradeDate Book Qty "
                                  "Unit UnitType Name Event Trade")


###############################################################################
class Transaction(UfoBase):
    """
    Transactions represent trading events:
    - Transactions are the only means to change positions. Positions effects
      associated to each transaction are two sided and must always sume to
      zero.
    - Each transaction refers to one and only one trade.
    - Each transaction has marker to define the its type and a pointer to the
      previous transaction in the chain.
    - Each transaction has marker to indentify the event that gave rise to its
      creation.
    """
    TransactionDate = DateField()
    SecurityTraded = ReferenceField(obj_type="TradableObj")
    Quantity = FloatField(default=0.0)
    Party = ReferenceField(obj_type="Book")
    Counterparty = ReferenceField(obj_type="Book")
    Trade = ReferenceField(obj_type="Trade")
    PrevTransaction = ReferenceField(obj_type="Transaction")
    Event = StringField()
    Marker = SelectField(options=["HEAD", "AMENDED", "AGED",
                                  "BACKOUT", "ROLLEDBACK", "DELETED"])

    # -------------------------------------------------------------------------
    def __post_init__(self):
        self.Name = self.Name or Transaction.random_name()

    # -------------------------------------------------------------------------
    @ValueType()
    def Denominated(self, graph):
        return graph(graph(self, "SecurityTraded"), "Denominated")

    # -------------------------------------------------------------------------
    @ValueType()
    def Trader(self, graph):
        return graph(graph(self, "Trade"), "Trader")

    # -------------------------------------------------------------------------
    @ValueType()
    def TransactionInfo(self, graph):
        """
        Return a dictionary {attribute: value}, including only the stored
        attributes that can be altered by a transaction amendment.
        """
        attrs = self._json_fields.copy()
        attrs = sorted(attrs.difference({"Trade", "Event", "Marker"}))
        return dict(zip(attrs, [graph(self, attr) for attr in attrs]))

    # -------------------------------------------------------------------------
    @ValueType()
    def Leaves(self, graph):
        qty = graph(self, "Quantity")
        sec = graph(self, "SecurityTraded")
        return qty*graph(sec, "Leaves")

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
        ccy = graph(self, "Denominated")
        spot_fx = graph("{0:3s}/USD".format(ccy), "Spot")
        return graph(self, "MktValUSD") / spot_fx

    # -------------------------------------------------------------------------
    @ValueType()
    def PositionEffects(self, graph):
        sec = graph(self, "SecurityTraded")
        qty = graph(self, "Quantity")
        date = graph(self, "TransactionDate")
        name = graph(self, "Name")
        event = graph(self, "Event")
        trade = graph(self, "Trade")
        cpty1 = graph(self, "Party")
        cpty2 = graph(self, "Counterparty")

        pos_effects = [
            Position(date, cpty1, qty,
                     sec, graph(sec, "ObjType"), name, event, trade),
            Position(date, cpty2, -qty,
                     sec, graph(sec, "ObjType"), name, event, trade)
        ]

        return pos_effects

    # -------------------------------------------------------------------------
    def delete(self):
        if GetVal("Database", "TradesDeletable"):
            query = """DELETE FROM PosEffects WHERE Transaction=%s;
                       NOTIFY PosEffects, %s; NOTIFY PosEffects, %s;"""
            ObjDbQuery(query, parms=(self.Name, self.Party, self.Counterparty))
        else:
            raise TransactionError("Trying to delete a "
                                   "transaction without permission")

    # -------------------------------------------------------------------------
    @classmethod
    def random_name(cls):
        return "TmpTrs-{0:>07d}".format(random.randrange(0, 10000000, 1))

    # -------------------------------------------------------------------------
    @classmethod
    def format_name(cls, date, trd_id):
        return "TRS {0:s} {1:s}".format(date.strftime("%Y%m%d"), trd_id)
