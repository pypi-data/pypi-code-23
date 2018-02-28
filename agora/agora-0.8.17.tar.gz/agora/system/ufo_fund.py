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

from onyx.core import (Archivable, ValueType,
                       ReferenceField, StringField, FloatField)

from onyx.core import (MktIndirectionFactory, EnforceArchivableEntitlements)

from agora.risk.core_functions import WithRiskValueTypes

__all__ = ["Fund"]


###############################################################################
@WithRiskValueTypes
@EnforceArchivableEntitlements("Database", "ArchivedOverwritable")
class Fund(Archivable):
    """
    Class used to represent an investment Fund.
    """
    # --- base currency for the whole fund
    Denominated = ReferenceField(obj_type="Currency")
    # --- this portfolio captures all investments
    Portfolio = ReferenceField(obj_type="Portfolio")
    # --- this book captures subscriptions/redemptions as well as costs and
    #     amortized costs
    CashAccount = ReferenceField(obj_type="Book")
    DisplayName = StringField()

    # -------------------------------------------------------------------------
    @ValueType()
    def Leaves(self, graph):
        port_leaves = graph(graph(self, "Portfolio"), "Leaves")
        cash_leaves = graph(graph(self, "CashAccount"), "Leaves")
        return port_leaves + cash_leaves

    # -------------------------------------------------------------------------
    @ValueType()
    def MktValUSD(self, graph):
        port_mtm = graph(graph(self, "Portfolio"), "MktValUSD")
        cash_mtm = graph(graph(self, "CashAccount"), "MktValUSD")
        return port_mtm + cash_mtm

    # -------------------------------------------------------------------------
    @ValueType()
    def MktVal(self, graph):
        denominated = graph(self, "Denominated")
        spot_fx = graph("{0:3s}/USD".format(denominated), "Spot")
        return graph(self, "MktValUSD") / spot_fx

    # -------------------------------------------------------------------------
    @MktIndirectionFactory(FloatField)
    def Nav(self, graph):
        pass

    # -------------------------------------------------------------------------
    @MktIndirectionFactory(FloatField)
    def Gav(self, graph):
        pass

    # -------------------------------------------------------------------------
    @MktIndirectionFactory(FloatField)
    def Aum(self, graph):
        pass

    # -------------------------------------------------------------------------
    @MktIndirectionFactory(FloatField)
    def NumberOfShares(self, graph):
        pass

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def NavCurve(self, graph, start=None, end=None):
        return self.get_history("Nav", start, end)

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def GavCurve(self, graph, start=None, end=None):
        return self.get_history("Gav", start, end)

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def AumCurve(self, graph, start=None, end=None):
        return self.get_history("Aum", start, end)
