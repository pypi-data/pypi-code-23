import unittest
from wml_runner import *


if __name__ == '__main__':
    test_cases = unittest.TestLoader().discover(start_dir="../svt", pattern="test_scikit*.py")

    runner = WMLRunner(test_cases=test_cases, environment="SVT", passrate_filename="reliability", test_output_dir="reliability")
    runner.run()
