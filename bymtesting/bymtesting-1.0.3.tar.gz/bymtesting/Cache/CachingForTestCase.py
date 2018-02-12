import datetime
#from service.webApiSetupService import *
from bymtesting.Cache.DockerTestCacheService import *
from bymtesting.Seed.SeedDataTemplate import *


class CachingForTestCase():

    # Denne funksjonen bytter IKKE ut Database Containeren
    def setUp_use_cached_only_populate(self, testdata):
        testdata.populate(useCache=True)

    def setUp_use_cached(self, testdata):
        DockerTestCacheService(testdata).resetOnlyInitializedDatabase()
        testdata.populate(useCache=True)

    def setUp_use_non_cached(self, testdata):
        # webApiSetupService().setupwebApiWithAutentisering()
        testdata.populate(useCache=False)

    def setUp_delete_all_containers_pull_new_restart_everything_and_populate(self, testdata):
        DockerTestCacheService(testdata).updateTestCache()
        testdata.populate(useCache=True)
