# encoding: utf-8
# encoding: utf-8

import logging_helper
import unittest
from conversionutil import dictify
from conversionutil import storage

logging = logging_helper.setup_logging()


class TestConvertStorageSize(unittest.TestCase):
    def setUp(self):
        self.fn = storage.convert_storage_size

    def tearDown(self):
        pass

    def do_assert(self,
                  input_value,
                  input_units,
                  output_units,
                  expected):
        result = self.fn(value=input_value,
                         input_units=input_units,
                         output_units=output_units)
        self.assertEqual(result,
                         expected,
                         (u"value:{value}; input_units:{input_units}; output_units:{output_units}; "
                          u"expected:{expected}; actual:{actual}"
                          .format(value=input_value,
                                  input_units=input_units,
                                  output_units=output_units,
                                  expected=expected,
                                  actual=result)))

    def si_asserts_from_bytes(self,
                              input_unit,
                              output_unit,
                              power):

        pwr = 10 ** power

        for params in [dictify(input_value=-2 * pwr, expected=u'-2.00{u}'.format(u=output_unit)),
                       dictify(input_value=0, expected=u'0.00{u}'.format(u=output_unit)),
                       dictify(input_value=16 * pwr, expected=u'16.00{u}'.format(u=output_unit)),
                       dictify(input_value=16.5 * pwr, expected=u'16.50{u}'.format(u=output_unit)),
                       dictify(input_value=999.999 * pwr, expected=u'1000.00{u}'.format(u=output_unit)),
                       dictify(input_value=2500 * pwr, expected=u'2500.00{u}'.format(u=output_unit))
                       ]:
            self.do_assert(input_units=input_unit,
                           output_units=output_unit,
                           **params)

    def iec_asserts_from_bytes(self,
                               input_unit,
                               output_unit,
                               power):

        pwr = 2 ** power

        for params in [dictify(input_value=-2 * pwr, expected=u'-2.00{u}'.format(u=output_unit)),
                       dictify(input_value=0, expected=u'0.00{u}'.format(u=output_unit)),
                       dictify(input_value=16 * pwr, expected=u'16.00{u}'.format(u=output_unit)),
                       dictify(input_value=16.5 * pwr, expected=u'16.50{u}'.format(u=output_unit)),
                       dictify(input_value=999.999 * pwr, expected=u'1000.00{u}'.format(u=output_unit)),
                       dictify(input_value=2500 * pwr, expected=u'2500.00{u}'.format(u=output_unit))
                       ]:
            self.do_assert(input_units=input_unit,
                           output_units=output_unit,
                           **params)

    def si_asserts_to_bytes(self,
                            input_unit,
                            output_unit,
                            power):

        pwr = 10 ** power

        for params in [dictify(input_value=-2, expected=u'-{v}{u}'.format(v=2 * pwr, u=output_unit)),
                       dictify(input_value=0, expected=u'{v}{u}'.format(v=0 * pwr, u=output_unit)),
                       dictify(input_value=16, expected=u'{v}{u}'.format(v=16 * pwr, u=output_unit)),
                       dictify(input_value=16.5, expected=u'{v:.0f}{u}'.format(v=16.5 * pwr, u=output_unit)),
                       dictify(input_value=999.99, expected=u'{v:.0f}{u}'.format(v=999.99 * pwr, u=output_unit)),
                       dictify(input_value=2500, expected=u'{v}{u}'.format(v=2500 * pwr, u=output_unit))
                       ]:
            self.do_assert(input_units=input_unit,
                           output_units=output_unit,
                           **params)

    def iec_asserts_to_bytes(self,
                             input_unit,
                             output_unit,
                             power):

        pwr = 2 ** power

        for params in [dictify(input_value=-2, expected=u'-{v}{u}'.format(v=2 * pwr, u=output_unit)),
                       dictify(input_value=0, expected=u'{v}{u}'.format(v=0 * pwr, u=output_unit)),
                       dictify(input_value=16, expected=u'{v}{u}'.format(v=16 * pwr, u=output_unit)),
                       dictify(input_value=16.5, expected=u'{v:.0f}{u}'.format(v=16.5 * pwr, u=output_unit)),
                       dictify(input_value=999.99, expected=u'{v:.0f}{u}'.format(v=999.99 * pwr, u=output_unit)),
                       dictify(input_value=2500, expected=u'{v}{u}'.format(v=2500 * pwr, u=output_unit))
                       ]:
            self.do_assert(input_units=input_unit,
                           output_units=output_unit,
                           **params)

    # Test byte pass through
    def test_convert_storage_size_bytes_to_bytes(self):

        input_unit = output_unit = u'B'
        for params in [dictify(input_value=-2, expected=u'-2{u}'.format(u=output_unit)),
                       dictify(input_value=0, expected=u'0{u}'.format(u=output_unit)),
                       dictify(input_value=16, expected=u'16{u}'.format(u=output_unit)),
                       dictify(input_value=999, expected=u'999{u}'.format(u=output_unit)),
                       dictify(input_value=2500, expected=u'2500{u}'.format(u=output_unit))
                       ]:
            self.do_assert(input_units=input_unit,
                           output_units=output_unit,
                           **params)

    # Test output conversion
    def test_convert_storage_size_bytes_to_kilobytes(self):
        self.si_asserts_from_bytes(input_unit=u'B', output_unit=u'KB', power=3)

    def test_convert_storage_size_bytes_to_megabytes(self):
        self.si_asserts_from_bytes(input_unit=u'B', output_unit=u'MB', power=6)

    def test_convert_storage_size_bytes_to_gigabytes(self):
        self.si_asserts_from_bytes(input_unit=u'B', output_unit=u'GB', power=9)

    def test_convert_storage_size_bytes_to_terabytes(self):
        self.si_asserts_from_bytes(input_unit=u'B', output_unit=u'TB', power=12)

    def test_convert_storage_size_bytes_to_petabytes(self):
        self.si_asserts_from_bytes(input_unit=u'B', output_unit=u'PB', power=15)

    def test_convert_storage_size_bytes_to_kibibytes(self):
        self.iec_asserts_from_bytes(input_unit=u'B', output_unit=u'KiB', power=10)

    def test_convert_storage_size_bytes_to_mebibytes(self):
        self.iec_asserts_from_bytes(input_unit=u'B', output_unit=u'MiB', power=20)

    def test_convert_storage_size_bytes_to_gibibytes(self):
        self.iec_asserts_from_bytes(input_unit=u'B', output_unit=u'GiB', power=30)

    def test_convert_storage_size_bytes_to_tebibytes(self):
        self.iec_asserts_from_bytes(input_unit=u'B', output_unit=u'TiB', power=40)

    def test_convert_storage_size_bytes_to_pebibytes(self):
        self.iec_asserts_from_bytes(input_unit=u'B', output_unit=u'PiB', power=50)

    # Test input conversion
    def test_convert_storage_size_kilobytes_to_bytes(self):
        self.si_asserts_from_bytes(input_unit=u'B', output_unit=u'KB', power=3)

    def test_convert_storage_size_megabytes_to_bytes(self):
        self.si_asserts_to_bytes(input_unit=u'MB', output_unit=u'B', power=6)

    def test_convert_storage_size_gigabytes_to_bytes(self):
        self.si_asserts_to_bytes(input_unit=u'GB', output_unit=u'B', power=9)

    def test_convert_storage_size_terabytes_to_bytes(self):
        self.si_asserts_to_bytes(input_unit=u'TB', output_unit=u'B', power=12)

    def test_convert_storage_size_petabytes_to_bytes(self):
        self.si_asserts_to_bytes(input_unit=u'PB', output_unit=u'B', power=15)

    def test_convert_storage_size_kibibytes_to_bytes(self):
        self.iec_asserts_to_bytes(input_unit=u'KiB', output_unit=u'B', power=10)

    def test_convert_storage_size_mebibytes_to_bytes(self):
        self.iec_asserts_to_bytes(input_unit=u'MiB', output_unit=u'B', power=20)

    def test_convert_storage_size_gibibytes_to_bytes(self):
        self.iec_asserts_to_bytes(input_unit=u'GiB', output_unit=u'B', power=30)

    def test_convert_storage_size_tebibytes_to_bytes(self):
        self.iec_asserts_to_bytes(input_unit=u'TiB', output_unit=u'B', power=40)

    def test_convert_storage_size_pebibytes_to_bytes(self):
        self.iec_asserts_to_bytes(input_unit=u'PiB', output_unit=u'B', power=50)

    # Test combined conversion
    def test_convert_storage_size_megabytes_to_gigabytes(self):

        pwr = 10 ** 3
        input_unit = u'MB'
        output_unit = u'GB'

        self.assertEqual(self.fn(value=-2 * pwr, input_units=input_unit, output_units=output_unit),
                         u'-2.00{u}'.format(u=output_unit))
        self.assertEqual(self.fn(value=0, input_units=input_unit, output_units=output_unit),
                         u'0.00{u}'.format(u=output_unit))
        self.assertEqual(self.fn(value=16 * pwr, input_units=input_unit, output_units=output_unit),
                         u'16.00{u}'.format(u=output_unit))
        self.assertEqual(self.fn(value=16.5 * pwr, input_units=input_unit, output_units=output_unit),
                         u'16.50{u}'.format(u=output_unit))
        self.assertEqual(self.fn(value=999.99 * pwr, input_units=input_unit, output_units=output_unit, decimals=1),
                         u'1000.0{u}'.format(u=output_unit))
        self.assertEqual(self.fn(value=2500 * pwr, input_units=input_unit, output_units=output_unit),
                         u'2500.00{u}'.format(u=output_unit))

    # Test failure scenarios
    def test_convert_storage_size_invalid_input_unit(self):
        with self.assertRaises(ValueError):
            self.fn(value=10, input_units=u'A', output_units=u'B')

    def test_convert_storage_size_invalid_output_unit(self):
        with self.assertRaises(ValueError):
            self.fn(value=10, input_units=u'MB', output_units=u'A')


# TODO: Write these tests
class TestConvertToUnicode(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_x(self):
        pass


# TODO: Write these tests
class TestConvertDatetimeToEpoch(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_x(self):
        pass


# TODO: Write these tests
class TestConvertEpochToTime(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_x(self):
        pass


# TODO: Write these tests
class TestConvertGetConversion(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_x(self):
        pass


if __name__ == u'__main__':
    unittest.main()
