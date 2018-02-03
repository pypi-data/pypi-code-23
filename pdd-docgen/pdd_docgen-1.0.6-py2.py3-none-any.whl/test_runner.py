import unittest


class TestRunner:
    def run(self, tests):
        result = TestResult()
        tests(result)
        print()
        return result.results


class TestResult(unittest.TestResult):
    def __init__(self):
        self.results = []
        super().__init__()

    def addSuccess(self, test):
        print(".", end="", flush=True)
        info = test.docgen
        if info:
            self.results.append(info)

        unittest.TestResult.addSuccess(self, test)

    def addError(self, test, err):
        print(test)
        print(err)
        unittest.TestResult.addError(self, test, err)

    def addFailure(self, test, err):
        print(test)
        print(err)
        unittest.TestResult.addFailure(self, test, err)
