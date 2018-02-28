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

#from onyx.core import UfoBase, StringField, ListField, ObjDbQuery, GraphNodeVt
from onyx.core import ValueType as ValueTypeDecorator
from onyx.core import (ObjNamesByType,
                       UfoBase, StringField, ListField)

#import json

__all__ = ["Category"]

#GET_ITEMS = "SELECT Name FROM Objects WHERE ObjType IN %s AND Data @> %s;"


###############################################################################
class Category(UfoBase):
    """
    Class used to collect instances of classes listed in ObjTypes that match
    the following pattern:
        graph(instance, "ValueType") == graph(self, "TargetValue")
    """
    ObjTypes = ListField()
    ValueType = StringField()
    TargetValue = StringField()

    # -------------------------------------------------------------------------
    def __post_init__(self):
        self.TargetValue = self.TargetValue or self.Name

    # -------------------------------------------------------------------------
    @ValueTypeDecorator()
    def Items(self, graph):
        vt = graph(self, "ValueType")
        value = graph(self, "TargetValue")
        types = graph(self, "ObjTypes")
        names = [name for obj_type in types
                 for name in ObjNamesByType(obj_type)]
        return sorted([name for name in names if graph(name, vt) == value])

#    # -------------------------------------------------------------------------
#    @ValueTypeDecorator()
#    def Items(self, graph):
#        parms = [tuple(graph(self, "ObjTypes"))]
#        if graph(self, "ValueType") is None:
#            parms += [json.dumps({})]
#        else:
#            parms += [json.dumps({
#                graph(self, "ValueType"): graph(self, "TargetValue")})]
#        results = ObjDbQuery(GET_ITEMS, parms, attr="fetchall")
#        return sorted([res.name for res in results])


# -----------------------------------------------------------------------------
def prepare_for_test():
    from onyx.core import AddIfMissing

    AddIfMissing(Category(Name="Nth. America",
                          ObjTypes=["EquityAsset"], ValueType="Region"))
    AddIfMissing(Category(Name="Nth. Europe",
                          ObjTypes=["EquityAsset"], ValueType="Region"))
    AddIfMissing(Category(Name="Cnt. Europe",
                          ObjTypes=["EquityAsset"], ValueType="Region"))

    AddIfMissing(Category(Name="USA",
                          ObjTypes=["EquityAsset"], ValueType="Country"))
    AddIfMissing(Category(Name="United Kingdom",
                          ObjTypes=["EquityAsset"], ValueType="Country"))
    AddIfMissing(Category(Name="Germany",
                          ObjTypes=["EquityAsset"], ValueType="Country"))
