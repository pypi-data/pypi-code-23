
import datetime as dt
import pandas as pd

from pandas.tseries.offsets import CustomBusinessDay
from pandas.tseries.holiday import USFederalHolidayCalendar


class Calendar:
    """
    """

    def __init__(self):
        """
        """
        self.HOLIDAY_CALENDAR = USFederalHolidayCalendar()
        self.BDAY_US = CustomBusinessDay(calendar=self.HOLIDAY_CALENDAR)

    def fmt_date(self, ts):
        """
        """
        if isinstance(ts, str):
            ts = pd.Timestamp(ts)
        if isinstance(ts, dt.datetime):
            ts = pd.to_datetime(ts)
        return ts

    def get_BD_fallback_next(self, ts):
        """
        """
        ts = self.fmt_date(ts)
        return ts + 0 * self.BDAY_US

    def get_BD_fallback_previous(self, ts):
        """
        """
        ts = self.fmt_date(ts)
        return ts + 1 * self.BDAY_US - 1 * self.BDAY_US


calendar = Calendar()
