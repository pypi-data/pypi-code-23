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

from onyx.core import IntField, FloatField, ValueType, Archivable
from onyx.core import MktIndirectionFactory, EnforceArchivableEntitlements


__all__ = ["NotificationRecord"]


###############################################################################
@EnforceArchivableEntitlements("Database", "ArchivedOverwritable")
class NotificationRecord(Archivable):
    """
    Class used to represent a notification of long or short interest in a
    security.
    """
    # -------------------------------------------------------------------------
    @MktIndirectionFactory(IntField)
    def Units(self, graph):
        pass

    # -------------------------------------------------------------------------
    @MktIndirectionFactory(FloatField)
    def Percentage(self, graph):
        pass

    # -------------------------------------------------------------------------
    @ValueType("PropSubGraph")
    def LastNotification(self, graph, date=None):
        date = date or graph("Database", "MktDataDate")
        dt_units, units = self.get_dated("Units", date, strict=False)
        dt_pct, pct = self.get_dated("Percentage", date, strict=False)
        return max(dt_units, dt_pct), units, pct
