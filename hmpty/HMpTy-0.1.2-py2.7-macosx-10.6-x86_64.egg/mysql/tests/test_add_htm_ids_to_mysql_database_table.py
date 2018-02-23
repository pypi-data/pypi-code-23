import os
import nose
import shutil
import yaml
from HMpTy import add_htm_ids_to_mysql_database_table, cl_utils
from HMpTy.utKit import utKit

from fundamentals import tools

su = tools(
    arguments={"settingsFile": None},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName="HMpTy",
    tunnel=False
)
arguments, settings, log, dbConn = su.setup()

# load settings
stream = file(
    "/Users/Dave/.config/HMpTy/HMpTy.yaml", 'r')
settings = yaml.load(stream)
stream.close()

# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()

from fundamentals.mysql import writequery
sqlQuery = """ALTER TABLE tcs_cat_ned_d_v10_2_0 DROP COLUMN cz, DROP COLUMN cy, DROP COLUMN cx, DROP COLUMN htm16ID, DROP COLUMN htm20ID"""
writequery(
    log=log,
    sqlQuery=sqlQuery,
    dbConn=dbConn
)


class test_add_htm_ids_to_mysql_database_table():

    def test_add_htm_ids_to_mysql_database_table_function(self):

        from HMpTy import add_htm_ids_to_mysql_database_table
        this = add_htm_ids_to_mysql_database_table(
            log=log,
            settings=settings
        )
        this.get()

    # def test_add_htm_ids_to_mysql_database_table_function_exception(self):

    #     from HMpTy import add_htm_ids_to_mysql_database_table
    #     try:
    #         this = add_htm_ids_to_mysql_database_table(
    #             log=log,
    #             settings=settings,
    #             fakeKey="break the code"
    #         )
    #         this.get()
    #         assert False
    #     except Exception, e:
    #         assert True
    #         print str(e)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
