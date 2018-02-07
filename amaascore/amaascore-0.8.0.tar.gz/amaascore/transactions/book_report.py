from decimal import Decimal
import json
from amaascore.core.amaas_model import AMaaSModel


class BookReport(AMaaSModel):

    def __init__(self, asset_manager_id, book_id, period, business_date, report_timestamp,
                 report_status='Active', currency=None, total_pnl=None, asset_pnl=None, fx_pnl=None, 
                 mtm_value=None, report_type=None, message=None, *args, **kwargs):
        
        self.asset_manager_id = asset_manager_id
        self.book_id = book_id
        self.period = period
        self.business_date = business_date
        self.currency = currency
        self.total_pnl = total_pnl
        self.asset_pnl = asset_pnl
        self.fx_pnl = fx_pnl
        self.report_status = report_status
        self.message = message
        self.mtm_value = mtm_value
        self.report_timestamp = report_timestamp
        self.report_type = report_type

        super(BookReport, self).__init__(*args, **kwargs)

    @property
    def report_type(self):
        return self._report_type

    @report_type.setter
    def report_type(self, val):
        if val not in ['MTM', 'PNL']:
            raise ValueError("""Unrecognized book report type: %s,
                            expect either 'MTM' or 'PNL'""" % str(val))
        self._report_type = val

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, val):
        if val not in ['YTD', 'MTD', 'DTD', 'N/A']:
            raise ValueError("""Unrecognized PnL period %s, expect
                    period to be one of the following: 'YTD', 'MTD', 'DTD', 'N/A'""" % str(val))
        self._period = val

    @property
    def total_pnl(self):
        return self._total_pnl

    @total_pnl.setter
    def total_pnl(self, val):
        if not isinstance(val, Decimal) and val is not None:
            self._total_pnl = Decimal(val)
        else:
            self._total_pnl = val

    @property
    def fx_pnl(self):
        return self._fx_pnl

    @fx_pnl.setter
    def fx_pnl(self, val):
        if not isinstance(val, Decimal) and val is not None:
            self._fx_pnl = Decimal(val)
        else:
            self._fx_pnl = val

    @property
    def asset_pnl(self):
        return self._asset_pnl

    @asset_pnl.setter
    def asset_pnl(self, val):
        if not isinstance(val, Decimal) and val is not None:
            self._asset_pnl = Decimal(val)
        else:
            self._asset_pnl = val

    @property
    def mtm_value(self):
        return self._mtm_value

    @mtm_value.setter
    def mtm_value(self, val):
        if not isinstance(val, Decimal) and val is not None:
            self._mtm_value = Decimal(val)
        else:
            self._mtm_value = val