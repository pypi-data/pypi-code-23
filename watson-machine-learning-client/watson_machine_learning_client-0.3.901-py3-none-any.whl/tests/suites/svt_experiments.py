import unittest
from wml_runner import *


if __name__ == '__main__':
    test_cases = unittest.TestLoader().discover(start_dir="../svt", pattern="test_experiment*.py")

    runner = WMLRunner(test_cases=test_cases, environment="SVT", passrate_filename="svt_experiments", test_output_dir="svt_experiments")
    runner.run()
