import os

class EnvironmentSetting:
    local = 'local'
    staging = 'staging'
    testing = 'testing'
    https = 'https'
    development = 'development'
    localdocker = 'localdocker'

    # UrlService.py skal alltid være deaktivert for denne verdien. 
    # production = 'production'


class EnvironmentService:

    def __init__(self):
        self.defaultValue = 'local'

    def getPythonEnv(self):
        return os.getenv('PYTHON_ENV', self.defaultValue)

    def setPythonEnv(self, python_env):
        os.environ["PYTHON_ENV"] = python_env       

    def getLocalDockerTargetEnv(self):
        if(self.getPythonEnv() != EnvironmentSetting.local or self.getPythonEnv() != EnvironmentSetting.localdocker):
            return self.getPythonEnv()
        if(os.getenv('LOCAL_DOCKER_TARGET_ENV') != None):
            print("LOCAL_DOCKER_TARGET_ENV is set locally to: " + os.getenv('LOCAL_DOCKER_TARGET_ENV'))
        return os.getenv('LOCAL_DOCKER_TARGET_ENV', self.getPythonEnv())

    def setLocalDockerTargetEnv(self, local_docker_target_env):
        os.environ["LOCAL_DOCKER_TARGET_ENV"] = local_docker_target_env      
       
    def isRunningInContainers(self):
        return self.getLocalDockerTargetEnv() == EnvironmentSetting().localdocker

    def printPythonEnv(self):
        print("PYTHON_ENV = {}".format(os.getenv('PYTHON_ENV')))
        print("LOCAL_DOCKER_TARGET_ENV = {}".format(os.getenv('LOCAL_DOCKER_TARGET_ENV')))
