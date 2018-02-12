# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.logging_utils import DEFAULT_LOGGING
from datetime import date
import random
import unittest

from amaascore.fundamentals.interface import FundamentalsInterface
from tests.unit.config import STAGE

import logging.config
logging.config.dictConfig(DEFAULT_LOGGING)


class FundamentalsInterfaceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fundamentals_interface = FundamentalsInterface(environment=STAGE)
        cls.asset_manager_id = random.randint(1, 2**31-1)

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure

    def tearDown(self):
        pass

    def test_Countries(self):
        country = self.fundamentals_interface.countries(country_code='SGP')
        self.assertEqual(country.get('name'), 'Singapore')

    def test_Holidays(self):
        this_year = date.today().year
        holidays = self.fundamentals_interface.holidays(country_codes=['USA', 'GBR'], years=[this_year, this_year+1])
        self.assertEqual(set(holidays.keys()), {'USA', 'GBR'})
        calendars = {holiday.get('calendar') for holiday in holidays.values()}
        self.assertEqual(calendars, {'UnitedStates', 'UnitedKingdom'})

    def test_BusinessDate(self):
        # Let's pretend the 1st May is an invalid settlement day for a hypothetical bond
        start_date = date(2017, 4, 28)  # This is a Friday
        mayday = [date(2017, 5, 1)]
        settlement_date = self.fundamentals_interface.calc_business_date(start_date=start_date, country_codes=['USA'],
                                                                         offset=2, invalid_dates=mayday)
        self.assertEqual(settlement_date, date(2017, 5, 3))  # 2 day offset + weekend + extra date

    def test_BusinessDateAcrossMultipleCalendars(self):
        start_date = date(2017, 4, 28)  # This is a Friday
        settlement_date = self.fundamentals_interface.calc_business_date(start_date=start_date, offset=2,
                                                                         country_codes=['USA', 'GBR'])
        self.assertEqual(settlement_date, date(2017, 5, 3))  # 2 day offset + weekend + UK holiday

    def test_GetDateInfo(self):
        business_date = date(2017, 4, 29)  # This is a Saturday
        date_info = self.fundamentals_interface.get_date_info(business_date=business_date,
                                                              country_codes=['USA', 'GBR'])
        self.assertEqual(date_info, {'USA': {'working_day': False}, 'GBR': {'working_day': False}})
        business_date = date(2017, 5, 1)  # This is a UK holiday
        date_info = self.fundamentals_interface.get_date_info(business_date=business_date,
                                                              country_codes=['USA', 'GBR'])
        self.assertEqual(date_info, {'USA': {'working_day': True}, 'GBR': {'working_day': False}})

if __name__ == '__main__':
    unittest.main()
