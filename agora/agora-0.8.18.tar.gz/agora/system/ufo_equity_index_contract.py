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

from onyx.core import (Date, Knot, Curve, HlocvCurve, LYY2Date, DateOffset,
                       GetVal, SetVal, DelObj, UpdateObj, ObjNotFound,
                       ValueType, DictField, StringField, ReferenceField,
                       InheritAsProperty, RetainedFactory)

from agora.system.ufo_asset import Asset

__all__ = ["EquityIndexCnt"]

# --- replace all base class stored attributes with pointers to EquityIndex,
#     with the exception of RiskProxy
REPLACE = Asset._json_fields.difference({"RiskProxy"})
# --- add a few EquityIndex-specific stored attributes
REPLACE = REPLACE.union({"Country", "Region",
                         "Sector", "Subsector", "ContractSize"})


###############################################################################
@InheritAsProperty(REPLACE, "EquityIndex")
class EquityIndexCnt(Asset):
    """
    This class used to access equity-index contract information and the
    relative price marks.
    """
    # --- this is the parent object that babysits all contracts on the same
    #     commodity
    EquityIndex = ReferenceField(obj_type="EquityIndex")

    # --- DeliveryMonth is the LYY code for the contract
    DeliveryMonth = StringField()

    Tickers = DictField()
    Marks = StringField()

    # -------------------------------------------------------------------------
    def __post_init__(self):
        sym = GetVal(self.EquityIndex, "Symbol")
        args = sym, self.DeliveryMonth

        self.Name = self.get_name(*args)
        self.Marks = "CNT-MKS {0:s} {1:3s}".format(*args)

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def Ticker(self, graph, platform="Bloomberg"):
        """
        If ticker for a given platform is missing, it's understood that we
        should default to the one for Bloomberg.
        """
        try:
            return graph(self, "Tickers")[platform]
        except KeyError:
            return graph(self, "Tickers")["Bloomberg"]

    # -------------------------------------------------------------------------
    @ValueType()
    def UniqueId(self, graph):
        sym = graph(self, "Symbol")
        mth = graph(self, "DeliveryMonth")
        return "{0:s} {1:3s}".format(sym, mth)

    # -------------------------------------------------------------------------
    @ValueType()
    def FutSettDate(self, graph):
        rule = graph(self, "SettDateRule")
        cal = graph(self, "HolidayCalendar")
        mth = graph(self, "DeliveryMonth")
        return DateOffset(LYY2Date(mth), rule, cal)

    # -------------------------------------------------------------------------
    @ValueType()
    def VolEndDate(self, graph):
        return graph(self, "FutSettDate")

    # -------------------------------------------------------------------------
    @ValueType()
    def OptExpDate(self, graph):
        rule = graph(self, "OptExpDateRule")
        cal = graph(self, "HolidayCalendar")
        return DateOffset(graph(self, "FutSettDate"), rule, cal)

    # -------------------------------------------------------------------------
    @RetainedFactory()
    def Spot(self, graph):
        """
        Return the official close value as of MktDataDate (or the most recent
        close if ForceStrict is False) in the Denominated currency.
        """
        return graph(graph(self, "Marks"), "Price")*graph(self, "Multiplier")

    # -------------------------------------------------------------------------
    @ValueType()
    def Last(self, graph):
        """
        Return the knot with the most recent close value (irrespective of
        MktDataDate) in the Denominated currency.
        """
        marks = graph(self, "Marks")
        date, value = graph(marks, "LastKnot", date=Date.high_date())
        return Knot(date, value*graph(self, "Multiplier"))

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def GetMarks(self, graph, start=None, end=None):
        return graph(graph(self, "Marks"), "PrcFixCurve", start=start, end=end)

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def GetCurve(self, graph, start=None, end=None, field=None):
        if field == "Close":
            return graph(self, "GetMarks", start=start, end=end)
        else:
            return HlocvCurve() if field is None else Curve()

    # -------------------------------------------------------------------------
    def delete(self):
        # --- delete price fixes
        try:
            DelObj(self.Marks)
        except ObjNotFound:
            pass

        # --- remove from set of contracts for the CommodAsset object
        cnts = GetVal(self.EquityIndex, "Contracts")
        cnts.discard(self.DeliveryMonth)

        SetVal(self.EquityIndex, "Contracts", cnts)
        UpdateObj(self.EquityIndex)

    # -------------------------------------------------------------------------
    @classmethod
    def get_name(cls, symbol, del_mth):
        """
        Generate contract's name from Symbol, and DeliveryMonth
        """
        return "CNT {0:s} {1:3s}".format(symbol, del_mth)


# -----------------------------------------------------------------------------
def prepare_for_test():
    from onyx.core import Date, AddIfMissing, EvalBlock
    from agora.system.ufo_price_fix import PriceFix

    import agora.system.ufo_equity_index as ufo_equity_index
    import agora.system.ufo_price_fix as ufo_price_fix

    ufo_equity_index.prepare_for_test()
    ufo_price_fix.prepare_for_test()

    sx5e_z15_info = {
        "EquityIndex": "EQ-IDX SX5E",
        "DeliveryMonth": "Z15",
        "Tickers": {"Bloomberg": "VGZ5"},
    }

    cnt = AddIfMissing(EquityIndexCnt(**sx5e_z15_info))
    prc_fix = AddIfMissing(PriceFix(Name=GetVal(cnt, "Marks")))

    with EvalBlock() as eb:
        eb.change_value("Database", "ArchivedOverwritable", True)
        prc_fix.set_dated("Price", Date.today(), 3700.0)

    return [cnt.Name]
