import unittest
from bin_collection import *


class BinCollectionTestCases(unittest.TestCase):
    run_program_test()

    def test_get_bin_data_returns(self):
        self.assertTrue(get_bin_data() != "")

    def test_does_count_mode_occurances_returns_correct_numer(self):
        test_numbers = [[[1],[1],[1],[2],[2]], [[1],[1],[1],[1],[1]], [[1],[1],[1],[2],[2],[2]]]
        for numbers in test_numbers:
            self.assertTrue(count_the_mode_date_occurrences(numbers), 3)

    def test_does_input_date_get_validated_correctly(self):
        correct_dates = ["04/05/2018", "01/01/2017", "04/29/1988"]
        incorrect_dates = ["bob", "23/23/2323", "29/04/1988", "04.29.1988", "04-29-1988"]
        for date in correct_dates:
            self.assertTrue(is_date_valid(date))
        for date in incorrect_dates:
            self.assertFalse(is_date_valid(date) == False)

    def test_is_date_on_calendar_returns_true_when_date_exists(self):
        self.assertTrue(is_date_on_calendar("04/05/2018"))

    def test_is_date_on_calendar_returns_true_when_date_doesnt_exists(self):
        self.assertTrue(is_date_on_calendar("05/04/2018") == False)


def main():
    unittest.main()

if __name__ == '__main__':
    main()


