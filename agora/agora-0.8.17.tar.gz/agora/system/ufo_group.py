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

from onyx.core import ObjDbQuery
from onyx.core import ValueType, UfoBase
from onyx.core import ReferenceField, StringField

from agora.risk.core_functions import WithRiskValueTypes

import json

__all__ = ["Group"]

GET_ITEMS = "SELECT Name FROM Objects WHERE ObjType=Trader AND Data @> %s;"


###############################################################################
@WithRiskValueTypes
class Group(UfoBase):
    """
    Class used to represent a trading group.
    """
    Denominated = ReferenceField(obj_type="Currency")
    LongName = StringField()
    Portfolio = ReferenceField(obj_type="Portfolio")

    # -------------------------------------------------------------------------
    @ValueType()
    def Denominated(self, graph):
        return graph(self, "Portfolio")

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

    # -------------------------------------------------------------------------
    @ValueType()
    def Traders(self, graph):
        parms = (json.dumps({"Group": graph(self, "Name")}), )
        results = ObjDbQuery(GET_ITEMS, parms, attr="fetchall")
        return sorted([res.name for res in results])


# -----------------------------------------------------------------------------
def prepare_for_test():
    from onyx.core import AddIfMissing
    import agora.system.ufo_portfolio as ufo_portfolio

    portfolios = ufo_portfolio.prepare_for_test()

    groups = [
        AddIfMissing(Group(Name="TEST_GROUP", Portfolio=portfolios[0]))
    ]

    return [group.Name for group in groups]
