class TestData(object):
    def __init__(self,
                 ctx):
        self._ctx = ctx

    def create_license(self,
                       short_name = None):
        return self._ctx.gjp.testdata_create_license(short_name)

    def init_testcase(self,
                      testcase_id,
                      testrun_id):
        return self._ctx.gjp.testdata_init_testcase(testcase_id, testrun_id)
