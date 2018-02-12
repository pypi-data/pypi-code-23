from __future__ import absolute_import, division, print_function, unicode_literals

from dateutil.parser import parse
import sys

from amaascore.assets.asset import Asset

# This extremely ugly hack is due to the whole Python 2 vs 3 debacle.
type_check = str if sys.version_info >= (3, 0, 0) else (str, unicode)


class ForeignExchangeBase(Asset):
    """ This class should never be instantiated """

    def __init__(self, asset_id, asset_status, description, country_codes, display_name=None, currency=None,
                 asset_manager_id=0, *args, **kwargs):
        self.asset_class = 'ForeignExchange'
        self.country_codes = country_codes
        super(ForeignExchangeBase, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id, fungible=True,
                                                  display_name=display_name or asset_id, roll_price=False,
                                                  asset_status=asset_status, description=description, currency=currency,
                                                  *args, **kwargs)

    def base_currency(self):
        return self.asset_id[0:3]

    def counter_currency(self):
        return self.asset_id[3:6]

    def get_country_codes(self):
        return self.country_codes

    def get_currencies(self):
        return [self.base_currency(), self.counter_currency()]

    @property
    def country_codes(self):
        return self._country_codes

    @country_codes.setter
    def country_codes(self, country_codes):
        """

        :param country_codes:
        :return:
        """
        self._country_codes = country_codes

class ForeignExchange(ForeignExchangeBase):
    """
    The underlying FX pair used in an FX spot/forward asset
    """
    def __init__(self, asset_id, asset_manager_id=0, asset_status='Active', country_codes=[], major=False,
                 description='', *args, **kwargs):
        self.major = major
        super(ForeignExchange, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                              asset_status=asset_status, description=description,
                                              country_codes=country_codes,
                                              *args, **kwargs)

    @property
    def major(self):
        return self._major

    @major.setter
    def major(self, major):
        """

        :param major:
        :return:
        """
        if major:
            self._major = major
        else:
            self._major = False


class ForeignExchangeSpot(ForeignExchangeBase):
    """
    Spot FX (Settles as soon as possible).
    """

    def __init__(self, asset_manager_id, asset_id, asset_status='Active', description='', country_codes=[],
                 underlying=None, settlement_date=None, currency=None,
                 display_name=None, *args, **kwargs):
        super(ForeignExchangeSpot, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                                  asset_status=asset_status, currency=currency,
                                                  country_codes=country_codes, display_name=display_name,
                                                  description=description, *args, **kwargs)
        self.underlying = underlying
        self.settlement_date = settlement_date

    @property
    def settlement_date(self):
        return self._maturity_date

    @settlement_date.setter
    def settlement_date(self, settlement_date):
        self._maturity_date = parse(settlement_date).date() if isinstance(settlement_date, type_check) \
            else settlement_date

    def base_currency(self):
        return self.underlying[0:3] if self.underlying else None

    def counter_currency(self):
        return self.underlying[3:6] if self.underlying else None


class ForeignExchangeForward(ForeignExchangeSpot):
    """
    A forward-dated FX.  If there is a fixing_date, it is an NDF.
    """

    def __init__(self, asset_manager_id, asset_id, asset_status='Active', description='', country_codes=[],
                 forward_rate=None, underlying=None, settlement_date=None, fixing_date=None, currency=None,
                 display_name=None, *args, **kwargs):
        super(ForeignExchangeForward, self).__init__(asset_manager_id=asset_manager_id, asset_id=asset_id,
                                                     asset_status=asset_status, currency=currency,
                                                     underlying=underlying, settlement_date=settlement_date,
                                                     country_codes=country_codes, display_name=display_name,
                                                     description=description, *args, **kwargs)
        self.forward_rate = forward_rate
        self.fixing_date = fixing_date

    @property
    def fixing_date(self):
        return self._fixing_date

    @fixing_date.setter
    def fixing_date(self, fixing_date):
        self._fixing_date = parse(fixing_date).date() if isinstance(fixing_date, type_check) \
            else fixing_date


DIVISOR_TABLE = {
    'JPY': 100,
    'IDR': 1,
    'KRW': 1,
    'INR': 100,
    'THB': 100,
    'PHP': 1,
    'TWD': 1,
}
DEFAULT_DIVISOR = 10000


def calculate_rates(base_currency, counter_currency, forward_rate=None, fwd_points=None, spot_reference=None):
    """Calculate rates for Fx Forward based on others."""
    if base_currency not in DIVISOR_TABLE:
        divisor = DIVISOR_TABLE.get(counter_currency, DEFAULT_DIVISOR)
        if forward_rate is None and fwd_points is not None and spot_reference is not None:
            forward_rate = spot_reference + fwd_points / divisor
        elif forward_rate is not None and fwd_points is None and spot_reference is not None:
            fwd_points = (forward_rate - spot_reference) * divisor
        elif forward_rate is not None and fwd_points is not None and spot_reference is None:
            spot_reference = forward_rate - fwd_points / divisor

    rates = {}
    if forward_rate is not None:
        rates['forward_rate'] = forward_rate

    if fwd_points is not None:
        rates['fwd_points'] = fwd_points

    if spot_reference is not None:
        rates['spot_reference'] = spot_reference

    return rates
