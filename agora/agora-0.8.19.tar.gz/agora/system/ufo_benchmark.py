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

from onyx.core import Date, RDate, DateRange, Curve, Interpolate
from onyx.core import UfoBase, SetField, DictField, ValueType

import numpy as np

__all__ = ["Benchmark"]


###############################################################################
class Benchmark(UfoBase):
    """
    Container-like object use to represent a basket of equally weighted assets.
    """
    Symbols = SetField()
    FilterBy = DictField(default={})

    # -------------------------------------------------------------------------
    @ValueType()
    def FilteredSymbols(self, graph):
        symbols = graph(self, "Symbols")
        for attr, value in graph(self, "FilterBy").items():
            symbols = {sym for sym in symbols if graph(sym, attr) == value}
        return symbols

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def GetCurve(self, graph, start=None, end=None):
        start = start or Date.low_date()
        end = end or graph("Database", "MktDataDate")
        # --- we adjust the start date to make sure that we always have at
        #     least one knot in the curve before start date (this is needed
        #     by Interpolate)
        start_adj = start + RDate("-1w")

        dts = list(DateRange(start, end, "+1d"))
        returns = np.zeros(len(dts))

        # --- the basket is rewighted daily, hence we just need to calculate
        #     the series of average returns
        for sym in graph(self, "FilteredSymbols"):
            crv = graph(sym, "PricesForRisk", start_adj, end)
            vls = np.array([Interpolate(crv, d) for d in dts])
            returns[1:] += vls[1:] / vls[:-1] - 1.0

        num_of_symbols = len(graph(self, "FilteredSymbols"))
        if num_of_symbols:
            returns /= float(num_of_symbols)

        # --- the benchkmark is reconstructed from the series of returns
        return Curve(dts, np.cumprod(1.0 + returns))
