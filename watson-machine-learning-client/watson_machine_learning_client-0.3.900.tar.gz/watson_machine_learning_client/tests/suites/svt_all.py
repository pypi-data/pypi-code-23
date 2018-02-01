import unittest
from wml_runner import *


if __name__ == '__main__':
    test_cases = unittest.TestLoader().discover(start_dir="../svt", pattern="test*.py")

    runner = WMLRunner(test_cases=test_cases, environment="SVT", passrate_filename="svt_all", test_output_dir="svt_all")
    runner.run()
