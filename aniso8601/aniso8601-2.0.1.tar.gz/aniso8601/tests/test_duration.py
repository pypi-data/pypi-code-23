# -*- coding: utf-8 -*-

# Copyright (c) 2016, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import datetime
import unittest
import dateutil

from aniso8601.duration import parse_duration, _parse_duration_prescribed, \
        _parse_duration_combined, _parse_duration_prescribed_notime, \
        _parse_duration_prescribed_time, _parse_duration_element, \
        _has_any_component, _component_order_correct

class TestDurationParserFunctions(unittest.TestCase):
    def test_parse_duration(self):
        resultduration = parse_duration('P1Y2M3DT4H54M6S')
        self.assertEqual(resultduration, datetime.timedelta(days=428, seconds=17646))

        resultduration = parse_duration('P1Y2M3DT4H54M6.5S')
        self.assertEqual(resultduration, datetime.timedelta(days=428, seconds=17646.5))

        resultduration = parse_duration('P1Y2M3DT4H54M6,5S')
        self.assertEqual(resultduration, datetime.timedelta(days=428, seconds=17646.5))

        resultduration = parse_duration('P1Y2M3D')
        self.assertEqual(resultduration, datetime.timedelta(days=428))

        resultduration = parse_duration('P1Y2M3.5D')
        self.assertEqual(resultduration, datetime.timedelta(days=428.5))

        resultduration = parse_duration('P1Y2M3,5D')
        self.assertEqual(resultduration, datetime.timedelta(days=428.5))

        resultduration = parse_duration('PT4H54M6.5S')
        self.assertEqual(resultduration, datetime.timedelta(hours=4, minutes=54, seconds=6.5))

        resultduration = parse_duration('PT4H54M6,5S')
        self.assertEqual(resultduration, datetime.timedelta(hours=4, minutes=54, seconds=6.5))

        resultduration = parse_duration('P1Y')
        self.assertEqual(resultduration, datetime.timedelta(days=365))

        resultduration = parse_duration('P1.5Y')
        self.assertEqual(resultduration, datetime.timedelta(days=547.5))

        resultduration = parse_duration('P1,5Y')
        self.assertEqual(resultduration, datetime.timedelta(days=547.5))

        resultduration = parse_duration('P1M')
        self.assertEqual(resultduration, datetime.timedelta(days=30))

        resultduration = parse_duration('P1.5M')
        self.assertEqual(resultduration, datetime.timedelta(days=45))

        resultduration = parse_duration('P1,5M')
        self.assertEqual(resultduration, datetime.timedelta(days=45))

        resultduration = parse_duration('P1W')
        self.assertEqual(resultduration, datetime.timedelta(days=7))

        resultduration = parse_duration('P1.5W')
        self.assertEqual(resultduration, datetime.timedelta(days=10.5))

        resultduration = parse_duration('P1,5W')
        self.assertEqual(resultduration, datetime.timedelta(days=10.5))

        resultduration = parse_duration('P1D')
        self.assertEqual(resultduration, datetime.timedelta(days=1))

        resultduration = parse_duration('P1.5D')
        self.assertEqual(resultduration, datetime.timedelta(days=1.5))

        resultduration = parse_duration('P1,5D')
        self.assertEqual(resultduration, datetime.timedelta(days=1.5))

        resultduration = parse_duration('P0003-06-04T12:30:05')
        self.assertEqual(resultduration, datetime.timedelta(days=1279, hours=12, minutes=30, seconds=5))

        resultduration = parse_duration('P0003-06-04T12:30:05.5')
        self.assertEqual(resultduration, datetime.timedelta(days=1279, hours=12, minutes=30, seconds=5.5))

        #Verify overflows
        self.assertEqual(parse_duration('PT36H'), parse_duration('P1DT12H'))

    def test_parse_duration_nop(self):
        with self.assertRaises(ValueError):
            #Duration must start with a P
            parse_duration('1Y2M3DT4H54M6S')

    def test_parse_duration_weekcombination(self):
        with self.assertRaises(ValueError):
            #Week designator cannot be combined with other time designators
            #https://bitbucket.org/nielsenb/aniso8601/issues/2/week-designators-should-not-be-combinable
            parse_duration('P1Y2W')

    def test_parse_duration_outoforder(self):
        #Ensure durations are required to be in the correct order
        #https://bitbucket.org/nielsenb/aniso8601/issues/7/durations-with-time-components-before-t
        #https://bitbucket.org/nielsenb/aniso8601/issues/8/durations-with-components-in-wrong-order
        with self.assertRaises(ValueError):
            parse_duration('P1S')

        with self.assertRaises(ValueError):
            parse_duration('P1D1S')

        with self.assertRaises(ValueError):
            parse_duration('P1H1M')

        with self.assertRaises(ValueError):
            parse_duration('1Y2M3D1SPT1M')

        with self.assertRaises(ValueError):
            parse_duration('P1Y2M3D2MT1S')

        with self.assertRaises(ValueError):
            parse_duration('P2M3D1ST1Y1M')

        with self.assertRaises(ValueError):
            parse_duration('P1Y2M2MT3D1S')

        with self.assertRaises(ValueError):
            parse_duration('P1D1Y1M')

        with self.assertRaises(ValueError):
            parse_duration('PT1S1H')

    def test_parse_duration_suffixgarbage(self):
        #Don't allow garbage after the duration
        #https://bitbucket.org/nielsenb/aniso8601/issues/9/durations-with-trailing-garbage-are-parsed
        with self.assertRaises(ValueError):
            parse_duration('P1Dasdfasdf')

        with self.assertRaises(ValueError):
            parse_duration('P0003-06-04T12:30:05.5asdfasdf')

    def test_parse_duration_prescribed(self):
        resultduration = _parse_duration_prescribed('P1Y2M3DT4H54M6S', False)
        self.assertEqual(resultduration, datetime.timedelta(days=428, hours=4, minutes=54, seconds=6))

        resultduration = _parse_duration_prescribed('P1Y2M3DT4H54M6.5S', False)
        self.assertEqual(resultduration, datetime.timedelta(days=428, hours=4, minutes=54, seconds=6.5))

        resultduration = _parse_duration_prescribed('P1Y2M3DT4H54M6,5S', False)
        self.assertEqual(resultduration, datetime.timedelta(days=428, hours=4, minutes=54, seconds=6.5))

        resultduration = _parse_duration_prescribed('PT4H54M6.5S', False)
        self.assertEqual(resultduration, datetime.timedelta(hours=4, minutes=54, seconds=6.5))

        resultduration = _parse_duration_prescribed('PT4H54M6,5S', False)
        self.assertEqual(resultduration, datetime.timedelta(hours=4, minutes=54, seconds=6.5))

        resultduration = _parse_duration_prescribed('P1Y2M3D', False)
        self.assertEqual(resultduration, datetime.timedelta(days=428))

        resultduration = _parse_duration_prescribed('P1Y2M3.5D', False)
        self.assertEqual(resultduration, datetime.timedelta(days=428.5))

        resultduration = _parse_duration_prescribed('P1Y2M3,5D', False)
        self.assertEqual(resultduration, datetime.timedelta(days=428.5))

        resultduration = _parse_duration_prescribed('P1Y', False)
        self.assertEqual(resultduration, datetime.timedelta(days=365))

        resultduration = _parse_duration_prescribed('P1.5Y', False)
        self.assertEqual(resultduration, datetime.timedelta(days=547.5))

        resultduration = _parse_duration_prescribed('P1,5Y', False)
        self.assertEqual(resultduration, datetime.timedelta(days=547.5))

        resultduration = _parse_duration_prescribed('P1M', False)
        self.assertEqual(resultduration, datetime.timedelta(days=30))

        resultduration = _parse_duration_prescribed('P1.5M', False)
        self.assertEqual(resultduration, datetime.timedelta(days=45))

        resultduration = _parse_duration_prescribed('P1,5M', False)
        self.assertEqual(resultduration, datetime.timedelta(days=45))

        resultduration = _parse_duration_prescribed('P1W', False)
        self.assertEqual(resultduration, datetime.timedelta(days=7))

        resultduration = _parse_duration_prescribed('P1.5W', False)
        self.assertEqual(resultduration, datetime.timedelta(days=10.5))

        resultduration = _parse_duration_prescribed('P1,5W', False)
        self.assertEqual(resultduration, datetime.timedelta(days=10.5))

        resultduration = _parse_duration_prescribed('P1D', False)
        self.assertEqual(resultduration, datetime.timedelta(days=1))

        resultduration = _parse_duration_prescribed('P1.5D', False)
        self.assertEqual(resultduration, datetime.timedelta(days=1.5))

        resultduration = _parse_duration_prescribed('P1,5D', False)
        self.assertEqual(resultduration, datetime.timedelta(days=1.5))

        #Verify overflows
        self.assertEqual(parse_duration('PT36H'), parse_duration('P1DT12H'))

    def test_parse_duration_prescribed_multiplefractions(self):
        with self.assertRaises(ValueError):
            #Multiple fractions are not allowed
            _parse_duration_prescribed('P1Y2M3DT4H5.1234M6.1234S', False)

    def test_parse_duration_prescribed_middlefraction(self):
        with self.assertRaises(ValueError):
            #Fraction only allowed on final component
            _parse_duration_prescribed('P1Y2M3DT4H5.1234M6S', False)

    def test_parse_duration_prescribed_suffixgarbage(self):
        #Don't allow garbage after the duration
        #https://bitbucket.org/nielsenb/aniso8601/issues/9/durations-with-trailing-garbage-are-parsed
        with self.assertRaises(ValueError):
            _parse_duration_prescribed('P1Dasdfasdf', False)

    def test_parse_duration_prescribed_notime(self):
        resultduration = _parse_duration_prescribed_notime('P1Y2M3D')
        self.assertEqual(resultduration, (1, 2, 0, 3, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1Y2M3.5D')
        self.assertEqual(resultduration, (1, 2, 0, 3.5, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1Y2M3,5D')
        self.assertEqual(resultduration, (1, 2, 0, 3.5, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1Y')
        self.assertEqual(resultduration, (1, 0, 0, 0, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1.5Y')
        self.assertEqual(resultduration, (1.5, 0, 0, 0, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1,5Y')
        self.assertEqual(resultduration, (1.5, 0, 0, 0, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1M')
        self.assertEqual(resultduration, (0, 1, 0, 0, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1.5M')
        self.assertEqual(resultduration, (0, 1.5, 0, 0, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1,5M')
        self.assertEqual(resultduration, (0, 1.5, 0, 0, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1W')
        self.assertEqual(resultduration, (0, 0, 1, 0, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1.5W')
        self.assertEqual(resultduration, (0, 0, 1.5, 0, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1,5W')
        self.assertEqual(resultduration, (0, 0, 1.5, 0, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1D')
        self.assertEqual(resultduration, (0, 0, 0, 1, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1.5D')
        self.assertEqual(resultduration, (0, 0, 0, 1.5, 0, 0, 0))

        resultduration = _parse_duration_prescribed_notime('P1,5D')
        self.assertEqual(resultduration, (0, 0, 0, 1.5, 0, 0, 0))

    def test_parse_duration_prescribed_notime_timepart(self):
        #Ensure no time part is allowed
        with self.assertRaises(ValueError):
            _parse_duration_prescribed_notime('P1S')

        with self.assertRaises(ValueError):
            _parse_duration_prescribed_notime('P1D1S')

        with self.assertRaises(ValueError):
            _parse_duration_prescribed_notime('P1H1M')

        with self.assertRaises(ValueError):
            _parse_duration_prescribed_notime('P1Y2M3D4H')

        with self.assertRaises(ValueError):
            _parse_duration_prescribed_notime('P1Y2M3D4H5S')

    def test_parse_duration_prescribed_notime_outoforder(self):
        #Ensure durations are required to be in the correct order
        #https://bitbucket.org/nielsenb/aniso8601/issues/8/durations-with-components-in-wrong-order
        with self.assertRaises(ValueError):
            _parse_duration_prescribed_notime('P1H1M')

        with self.assertRaises(ValueError):
            _parse_duration_prescribed_notime('P1D1Y1M')

    def test_parse_duration_prescribed_time(self):
        resultduration = _parse_duration_prescribed_time('P1Y2M3DT4H54M6S')
        self.assertEqual(resultduration, (1, 2, 0, 3, 4, 54, 6))

        resultduration = _parse_duration_prescribed_time('P1Y2M3DT4H54M6.5S')
        self.assertEqual(resultduration, (1, 2, 0, 3, 4, 54, 6.5))

        resultduration = _parse_duration_prescribed_time('P1Y2M3DT4H54M6,5S')
        self.assertEqual(resultduration, (1, 2, 0, 3, 4, 54, 6.5))

        resultduration = _parse_duration_prescribed_time('PT4H54M6.5S')
        self.assertEqual(resultduration, (0, 0, 0, 0, 4, 54, 6.5))

        resultduration = _parse_duration_prescribed_time('PT4H54M6,5S')
        self.assertEqual(resultduration, (0, 0, 0, 0, 4, 54, 6.5))

    def test_parse_duration_prescribed_time_timeindate(self):
        #Don't allow time components in date half
        with self.assertRaises(ValueError):
            _parse_duration_prescribed_time('P1Y2M3D4HT54M6S')

        with self.assertRaises(ValueError):
            _parse_duration_prescribed_time('P1Y2M3D6ST4H54M')

    def test_parse_duration_prescribed_time_dateintime(self):
        #Don't allow date components in time half
        with self.assertRaises(ValueError):
            _parse_duration_prescribed_time('P2M3DT1Y4H54M6S')

        with self.assertRaises(ValueError):
            _parse_duration_prescribed_time('P1Y2MT3D4H54M6S')

    def test_parse_duration_prescribed_time_outoforder(self):
        #Ensure durations are required to be in the correct order
        #https://bitbucket.org/nielsenb/aniso8601/issues/7/durations-with-time-components-before-t
        with self.assertRaises(ValueError):
            _parse_duration_prescribed_time('1Y2M3D1SPT1M')

        with self.assertRaises(ValueError):
            _parse_duration_prescribed_time('P1Y2M3D2MT1S')

        with self.assertRaises(ValueError):
            _parse_duration_prescribed_time('P2M3D1ST1Y1M')

        with self.assertRaises(ValueError):
            _parse_duration_prescribed_time('P1Y2M2MT3D1S')

    def test_parse_duration_combined(self):
        resultduration = _parse_duration_combined('P0003-06-04T12:30:05', False)
        self.assertEqual(resultduration, datetime.timedelta(days=1279, hours=12, minutes=30, seconds=5))

        resultduration = _parse_duration_combined('P0003-06-04T12:30:05.5', False)
        self.assertEqual(resultduration, datetime.timedelta(days=1279, hours=12, minutes=30, seconds=5.5))

    def test_parse_duration_combined_suffixgarbage(self):
        #Don't allow garbage after the duration
        #https://bitbucket.org/nielsenb/aniso8601/issues/9/durations-with-trailing-garbage-are-parsed
        with self.assertRaises(ValueError):
            parse_duration('P0003-06-04T12:30:05.5asdfasdf')

    def test_parse_duration_element(self):
        self.assertEqual(_parse_duration_element('P1Y2M3D', 'Y'), 1)
        self.assertEqual(_parse_duration_element('P1Y2M3D', 'M'), 2)
        self.assertEqual(_parse_duration_element('P1Y2M3D', 'D'), 3)
        self.assertEqual(_parse_duration_element('T4H5M6.1234S', 'H'), 4)
        self.assertEqual(_parse_duration_element('T4H5M6.1234S', 'M'), 5)
        self.assertEqual(_parse_duration_element('T4H5M6.1234S', 'S'), 6.1234)
        self.assertEqual(_parse_duration_element('PT4H54M6,5S', 'H'), 4)
        self.assertEqual(_parse_duration_element('PT4H54M6,5S', 'M'), 54)
        self.assertEqual(_parse_duration_element('PT4H54M6,5S', 'S'), 6.5)

    def test_has_any_component(self):
        self.assertTrue(_has_any_component('P1Y', ['Y', 'M']))
        self.assertFalse(_has_any_component('P1Y', ['M', 'D']))

    def test_component_order_correct(self):
        self.assertTrue(_component_order_correct('P1Y1M1D', ['P', 'Y', 'M', 'D']))
        self.assertTrue(_component_order_correct('P1Y1M', ['P', 'Y', 'M', 'D']))
        self.assertFalse(_component_order_correct('P1D1Y1M', ['P', 'Y', 'M', 'D']))
        self.assertFalse(_component_order_correct('PT1S1H', ['T', 'H', 'M', 'S']))

class TestRelativeDurationParserFunctions(unittest.TestCase):
    def test_parse_duration_relative(self):
        resultduration = parse_duration('P1Y2M3DT4H54M6.5S', relative=True)
        self.assertEqual(resultduration, dateutil.relativedelta.relativedelta(years=1, months=2, days=3, hours=4, minutes=54, seconds=6.5))

        resultduration = parse_duration('P0003-06-04T12:30:05.5', relative=True)
        self.assertEqual(resultduration, dateutil.relativedelta.relativedelta(years=3, months=6, days=4, hours=12, minutes=30, seconds=5, microseconds=500000))

    def test_parse_duration_prescribed_relative(self):
        resultduration = _parse_duration_prescribed('P1Y', True)
        self.assertEqual(resultduration, dateutil.relativedelta.relativedelta(years=1))

        resultduration = _parse_duration_prescribed('P1M', True)
        self.assertEqual(resultduration, dateutil.relativedelta.relativedelta(months=1))

        #Add the relative ‘days’ argument to the absolute day. Notice that the ‘weeks’ argument is multiplied by 7 and added to ‘days’.
        #http://dateutil.readthedocs.org/en/latest/relativedelta.html
        resultduration = _parse_duration_prescribed('P1W', True)
        self.assertEqual(resultduration, dateutil.relativedelta.relativedelta(days=7))

        resultduration = _parse_duration_prescribed('P1.5W', True)
        self.assertEqual(resultduration, dateutil.relativedelta.relativedelta(days=10.5))

    def test_parse_duration_prescribed_relative_multiplefractions(self):
        with self.assertRaises(ValueError):
            #Multiple fractions are not allowed
            _parse_duration_prescribed('P1Y2M3DT4H5.1234M6.1234S', True)

    def test_parse_duration_prescribed_relative_middlefraction(self):
        with self.assertRaises(ValueError):
            #Fraction only allowed on final component
            _parse_duration_prescribed('P1Y2M3DT4H5.1234M6S', True)

    def test_parse_duration_prescribed_relative_suffixgarbage(self):
        #Don't allow garbage after the duration
        #https://bitbucket.org/nielsenb/aniso8601/issues/9/durations-with-trailing-garbage-are-parsed
        with self.assertRaises(ValueError):
            _parse_duration_prescribed('P1Dasdfasdf', True)

    def test_parse_duration_prescribed_relative_fractionalyear(self):
        #Fractional months and years are not defined
        #https://github.com/dateutil/dateutil/issues/40
        with self.assertRaises(ValueError):
            _parse_duration_prescribed('P1.5Y', True)

    def test_parse_duration_prescribed_relative_fractionalmonth(self):
        #Fractional months and years are not defined
        #https://github.com/dateutil/dateutil/issues/40
        with self.assertRaises(ValueError):
            _parse_duration_prescribed('P1.5M', True)

    def test_parse_duration_prescribed_relative_nodateutil(self):
        import sys
        import dateutil

        dateutil_import = dateutil

        sys.modules['dateutil'] = None

        with self.assertRaises(RuntimeError):
            _parse_duration_prescribed('P1Y', True)

        #Reinstall dateutil
        sys.modules['dateutil'] = dateutil

    def test_parse_duration_prescribed_relative_outoforder(self):
        #Ensure durations are required to be in the correct order
        #https://bitbucket.org/nielsenb/aniso8601/issues/7/durations-with-time-components-before-t
        #https://bitbucket.org/nielsenb/aniso8601/issues/8/durations-with-components-in-wrong-order
        with self.assertRaises(ValueError):
            _parse_duration_prescribed('P1S', True)

        with self.assertRaises(ValueError):
            _parse_duration_prescribed('P1D1S', True)

        with self.assertRaises(ValueError):
            _parse_duration_prescribed('P1H1M', True)

        with self.assertRaises(ValueError):
            _parse_duration_prescribed('1Y2M3D1SPT1M', True)

        with self.assertRaises(ValueError):
            _parse_duration_prescribed('P1Y2M3D2MT1S', True)

        with self.assertRaises(ValueError):
            _parse_duration_prescribed('P2M3D1ST1Y1M', True)

        with self.assertRaises(ValueError):
            _parse_duration_prescribed('P1Y2M2MT3D1S', True)

        with self.assertRaises(ValueError):
            _parse_duration_prescribed('P1D1Y1M', True)

        with self.assertRaises(ValueError):
            _parse_duration_prescribed('PT1S1H', True)

    def test_parse_duration_combined_relative(self):
        resultduration = _parse_duration_combined('P0003-06-04T12:30:05', True)
        self.assertEqual(resultduration, dateutil.relativedelta.relativedelta(years=3, months=6, days=4, hours=12, minutes=30, seconds=5))

        resultduration = _parse_duration_combined('P0003-06-04T12:30:05.5', True)
        self.assertEqual(resultduration, dateutil.relativedelta.relativedelta(years=3, months=6, days=4, hours=12, minutes=30, seconds=5, microseconds=500000))

    def test_parse_duration_combined_relative_suffixgarbage(self):
        #Don't allow garbage after the duration
        #https://bitbucket.org/nielsenb/aniso8601/issues/9/durations-with-trailing-garbage-are-parsed
        with self.assertRaises(ValueError):
            _parse_duration_combined('P0003-06-04T12:30:05.5asdfasdf', True)

    def test_parse_duration_combined_relative_nodateutil(self):
        import sys
        import dateutil

        dateutil_import = dateutil

        sys.modules['dateutil'] = None

        with self.assertRaises(RuntimeError):
            _parse_duration_combined('P0003-06-04T12:30:05', True)

        #Reinstall dateutil
        sys.modules['dateutil'] = dateutil
