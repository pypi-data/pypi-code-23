import os
import json
import docker
import pydash
import subprocess
import time
from bymtesting.Lib.EnvironmentService import *
from bymtesting.Autentisering.AutentiseringService import *
from bymtesting.WebApi.WebApiSetupService import *
from bymtesting.WebApi.WebApiServiceInfo import *


class DockerTestCacheService:

    def __init__(self, testdata):
        self.client = docker.from_env()
        self.autentiseringService = AutentiseringService(
            WebApiServiceInfo().webApiAdminNavn)
        self.environmentService = EnvironmentService()
        self.rootfolder = os.path.join(os.path.dirname(__file__))
        self.testdata = testdata

    def updateTestCache(self):
        if(self.environmentService.isRunningInContainers()):
            self.updateTestCacheWhenServicesAreRunningInContainers()
        else:
            self.updateTestCacheWhenServicesAreRunningOnWindowsHost()
        self.waitForDatabaseRestarting()
        self.waitForMicroservicesRestarting()

    def updateTestCacheWhenServicesAreRunningInContainers(self):
        # stopp og fjern alle database instanser på port 5432
        # docker-compose: start tom database på port 5432
        # populer database med grunndata
        # oppdater lokal cache
        # lag nytt Container image
        # stopp og fjern alle database instanser på 5432
        # start database med populerte data
        self.deleteContainersRunningWithPort5432ByForce()

        self.runCommand(
            "docker rmi bymdocker/postgresql-dev:populated", isCheck=False)
        self.runCommand(
            "docker-compose -f {}\docker-compose.new-db.yml pull".format(self.rootfolder))
        self.runCommand(
            "docker-compose -f {}\docker-compose.new-db.yml up -d".format(self.rootfolder))
        # Run Populate
        self.waitForDatabaseRestarting()
        self.waitForMicroservicesRestarting()
        self.populateDatabase()
        # Stopper containeren gracefully slik at nytt Container Image ikke blir
        # korrupt ift oppstart
        self.runCommand("docker stop postgresql_new")
        self.runCommand(
            "docker commit postgresql_new bymdocker/postgresql-dev:populated")
        self.deleteContainersRunningWithPort5432()
        self.runCommand(
            "docker-compose -f {}\docker-compose.populated-db.yml up -d".format(self.rootfolder))

    def updateTestCacheWhenServicesAreRunningOnWindowsHost(self):
        self.deleteContainersRunningWithPort5432ByForce()
        self.runCommand(
            "docker rmi bymdocker/postgresql-dev:populated", isCheck=False)
        self.runCommand(
            "docker-compose -f {}\docker-compose.new-db.yml pull bymlocaldb".format(self.rootfolder))
        self.runCommand(
            "docker-compose -f {}\docker-compose.new-db.yml up -d bymlocaldb".format(self.rootfolder))
        self.waitForDatabaseRestarting()
        # Fuuu.. Hvis jeg har slettet databasen, og IKKE restartet Servicene så vil ikke webApiService().getIsServiceRunning() fungere inntil Migrate har kjørt på nytt.
        # Servicene kjører allerede på Windows Host, men må vente på at databasen blir klar.
        # Dette gjelder selvsagt også når jeg sletter/bytter ut databasen når
        # jeg kjører Containerene.
        self.populateDatabase()
        self.runCommand("docker stop postgresql_new")
        self.runCommand(
            "docker commit postgresql_new bymdocker/postgresql-dev:populated")
        self.deleteContainersRunningWithPort5432()
        self.runCommand(
            "docker-compose -f {}\docker-compose.populated-db.yml up -d bymlocaldb".format(self.rootfolder))

    def populateDatabase(self):
        if(self.testdata == None):
            raise Exception(
                "No testdata to populate. Please provide DockerTestCacheService with testdata")
        WebApiSetupService().setupWebApiWithAutentisering()
        self.testdata.populate(useCache=True, updateCache=True)

    def runCommand(self, command, isCheck=True):
        print("\nRunning: {}".format(command))
        completedProcess = subprocess.run(command, shell=True, check=isCheck)
        return completedProcess
        # completedProcess = subprocess.run(command, shell=True, check=isCheck, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
        # print(completedProcess.stdout)
        # print(completedProcess.stderr)

    def deleteContainersRunningWithPort5432(self):
        containers = self.getContainersByPort5432()
        for container in containers:
            container.stop()
            container.remove()

    def deleteContainersRunningWithPort5432ByForce(self):
        containers = self.getContainersByPort5432()
        for container in containers:
            container.remove(force=True)

    def getContainersByPort5432(self):
        containers = self.client.containers.list(all=True)
        result = pydash.chain(containers).filter(
            lambda a: self.filterOnPort5432(a)).value()
        return result

    def isPopulatedDatabaseContainerImageCreated(self):
        imagename = "bymdocker/postgresql-dev:populated"
        result = self.client.images.list(name=imagename)
        return not result  # Returns True if found, False if the array is empty

    def filterOnPort5432(self, container):
        if(container.attrs["HostConfig"]["PortBindings"] == None):
            return False
        keys = container.attrs["HostConfig"]["PortBindings"].keys()
        for key in keys:
            if("5432" in key):
                return True
        return False

    def waitForMicroservicesRestarting(self):
        numberRetries = 0
        numberRetriesMax = 10
        while WebApiService().getIsServiceRunning() == False and self.autentiseringService.getIsServiceRunning() == False:
            if (numberRetries == numberRetriesMax):
                raise Exception(
                    'webApiService not running. Error connecting to the service')
            numberRetries = numberRetries + 1
            print("Waiting 2sec x {}".format(numberRetries))
            time.sleep(2)

        numberRetries = 0
        numberRetriesMax = 10
        while WebApiService().getIsServiceRunningWithDatabase() == False and self.autentiseringService.getIsServiceRunningWithDatabase() == False:
            if (numberRetries == numberRetriesMax):
                raise Exception(
                    'getIsServiceRunningWithDatabase not running. Error connecting to the service')
            numberRetries = numberRetries + 1
            print("Waiting 2sec x {}".format(numberRetries))
            time.sleep(2)

    def isDatabaseReady(self):
        result = self.runCommand("pg_isready", isCheck=False)
        return result.returncode == 0

    def waitForDatabaseRestarting(self):
        numberRetries = 0
        numberRetriesMax = 50
        while self.isDatabaseReady() == False:
            if (numberRetries == numberRetriesMax):
                raise Exception('Error starting Database')
            numberRetries = numberRetries + 1
            print("Waiting 2 sec x {}".format(numberRetries))
            time.sleep(2)

    def resetOnlyInitializedDatabase(self):
        # stopp og fjern alle database instanser på 5432
        # start database med populerte data
        # self.runCommand("docker-compose -f {}\docker-compose.populated-db.yml rm --stop --force bymlocaldb".format(self.rootfolder))
        if (self.isPopulatedDatabaseContainerImageCreated()):
            raise Exception(
                'Populated database image is not created. Run DockerTestCacheService=>updateTestCache()')
        self.deleteContainersRunningWithPort5432ByForce()
        # self.runCommand("docker-compose -f {}\docker-compose.populated-db.yml up -d --no-recreate bymlocaldb".format(self.rootfolder))
        if(self.environmentService.isRunningInContainers()):
            self.runCommand(
                "docker-compose -f {}\docker-compose.populated-db.yml up -d --no-recreate".format(self.rootfolder))
            self.waitForDatabaseRestarting()
            self.waitForMicroservicesRestarting()
        else:
            # when all services are running on Windows Host, then only start
            # the database container
            self.runCommand(
                "docker-compose -f {}\docker-compose.populated-db.yml up -d bymlocaldb".format(self.rootfolder))
            self.waitForDatabaseRestarting()
            self.waitForMicroservicesRestarting()

    def resetContainerServicesAndDatabase(self):
        # stopp og fjern alle database instanser på 5432
        # start database med populerte data
        if (self.isPopulatedDatabaseContainerImageCreated()):
            raise Exception(
                'Populated database image is not created. Run  DockerTestCacheService=>updateTestCache()')
        self.runCommand(
            "docker-compose -f {}\docker-compose.populated-db.yml down".format(self.rootfolder))
        self.runCommand(
            "docker-compose -f {}\docker-compose.populated-db.yml up -d".format(self.rootfolder))
        self.waitForDatabaseRestarting()
        self.waitForMicroservicesRestarting()
