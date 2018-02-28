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

from onyx.core import Structure
from onyx.core import ValueType, UfoBase, CreateInMemory
from onyx.core import ReferenceField, StringField, ListField

from agora.system.ufo_portfolio import Portfolio
from agora.risk.core_functions import WithRiskValueTypes

__all__ = ["PortfolioManager"]


###############################################################################
@WithRiskValueTypes
class PortfolioManager(UfoBase):
    """
    Class used to represent a portfolio manager of multiple funds.
    """
    Denominated = ReferenceField(obj_type="Currency")
    LongName = StringField()
    Funds = ListField()

    # -------------------------------------------------------------------------
    @ValueType()
    def Portfolio(self, graph):
        name = "{0:s} - TOP PORTFOLIO".format(graph(self, "Name"))
        kids = {graph(fund, "Portfolio"): 1 for fund in graph(self, "Funds")}
        ccy = graph(self, "Denominated")
        port = Portfolio(Name=name, Children=Structure(kids), Denominated=ccy)
        port = CreateInMemory(port)
        return port.Name

    # -------------------------------------------------------------------------
    @ValueType()
    def Aum(self, graph):
        ccyGroup = graph(self, "Denominated")
        ccyGroup2usd = graph("{0:3s}/USD".format(ccyGroup), "Spot")
        aum = 0.0
        for fund in graph(self, "Funds"):
            ccyFund = graph(fund, "Denominated")
            ccyFund2usd = graph("{0:3s}/USD".format(ccyFund), "Spot")
            aum +=  graph(fund, "Aum")*ccyFund2usd/ccyGroup2usd
        return aum

    # -------------------------------------------------------------------------
    @ValueType()
    def Leaves(self, graph):
        return graph(graph(self, "Portfolio"), "Leaves")

    # -------------------------------------------------------------------------
    @ValueType()
    def MktValUSD(self, graph):
        return graph(graph(self, "Portfolio"), "MktValUSD")

    # -------------------------------------------------------------------------
    @ValueType()
    def MktVal(self, graph):
        return graph(graph(self, "Portfolio"), "MktVal")


# -----------------------------------------------------------------------------
def prepare_for_test():
    pass
