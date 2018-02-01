import os
import unittest
import timeit
import sys
import xmlrunner
from datetime import timedelta

from os.path import join as path_join


class WMLRunner:
    test_cases = []
    test_total = 0
    test_failed = 0
    test_succeeded = 0
    test_skipped = 0
    duration = timeit.default_timer()
    passrate_file = None
    passrate_filename = ""
    test_output_dir = ""

    def __init__(self, test_cases, environment, spark_required=True, java_required=True,
                 passrate_filename="passrate", test_output_dir="test-reports"):

        self.test_cases = test_cases
        self.passrate_filename = passrate_filename
        self.test_output_dir = test_output_dir

        if environment is not None:
            os.environ['ENV'] = environment

        if spark_required:
            if "SPARK_HOME" not in os.environ:
                print("Test suite interrupted, reason: SPARK_HOME is not set")
                quit()

            SPARK_HOME_PATH = os.environ['SPARK_HOME']
            PYSPARK_PATH = str(SPARK_HOME_PATH) + "/python/"
            sys.path.insert(1, path_join(PYSPARK_PATH))

        if java_required:
            if "JAVA_HOME" not in os.environ:
                print("Test suite interrupted, reason: JAVA_HOME is not set")
                quit()

    def run(self):
        run_started_at = timeit.default_timer()
        runner = xmlrunner.XMLTestRunner(output="results/{}".format(self.test_output_dir))

        for test_case in self.test_cases:
            test_case_result = runner.run(test_case)

            self.test_total += test_case_result.testsRun
            self.test_failed += len(test_case_result.errors)
            self.test_skipped += len(test_case_result.skipped)

        self.duration = timeit.default_timer() - run_started_at
        self.test_succeeded = self.test_total - self.test_failed

        self._save_results_to_passrate_file()

    def _format_duration_output(self):
        duration_delta = timedelta(seconds=self.duration)
        duration_output = ""

        if duration_delta.seconds // 3600 >= 0:
            duration_output += "{}hrs ".format(duration_delta.seconds // 3600)

        if duration_delta.seconds // 60 >= 0:
            duration_output += "{}mts ".format(duration_delta.seconds // 60 % 60)

        if duration_delta.seconds >= 0:
            duration_output += "{}sec".format(duration_delta.seconds % 60)

        return duration_output

    def _save_results_to_passrate_file(self):
        self._create_passrate_file()
        self._save_passrate_file()

    def _create_passrate_file(self):
        self.passrate_file = open("results/{}.prop".format(self.passrate_filename), "w")

    def _save_passrate_file(self):

        if self.test_total == 0:
            self.passrate_file.write("PASSRATE20={:05.2f}\n".format(0))
        else:
            self.passrate_file.write("PASSRATE20={:05.2f}\n".format(self.test_succeeded / self.test_total * 100))

        self.passrate_file.write("Ignored_Tc={}\n".format(self.test_skipped))
        self.passrate_file.write("Succeeded={}\n".format(self.test_succeeded))
        self.passrate_file.write("Failed={}\n".format(self.test_failed))
        self.passrate_file.write("Total_Testcase={}\n".format(self.test_total))
        self.passrate_file.write("Duration={}\n".format(self._format_duration_output()))

        self.passrate_file.close()


def create_suite(test_module):
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromModule(module=test_module))
    return test_suite
