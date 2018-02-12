"""
    Fitchain connector - Fitchain SDK

    Client application to connect to the fitchain API
    Compatible with Python2,2.7,3.x

    :copyright: (c) 2018 fitchain.io
"""
import requests
import yaml
from pathlib import Path
from fitchain import dummy_data as dd
from fitchain.project import Project


class Runtime:
    def __init__(self, file="./.fitchain"):
        """
        Read the .fitchain yaml file to see which project we are dealing with.
        """
        config_file = Path(file)

        if not config_file.is_file():
            raise ValueError("The config file " + file + " could not be opened")

        with open(file, 'r') as stream:
            config = yaml.load(stream)

            if config["pod"] is None:
                raise ValueError("No pod address has been set within the config file")

            if config["projectId"] is None:
                raise ValueError("No projectId has been set within the config file")

        self.pod = Pod(config["pod"])
        self.project = self.pod.project(config["projectId"])


class Pod:
    def __init__(self, url="http://localhost:9400/v1"):
        self.base_url = url

    def identity(self):
        r = requests.get(self.base_url + '/gateway')

        return r.json()

    def project(self, id):
        r = requests.get(self.base_url + '/projects/' + id)

        return Project(**r.json())

    def projects(self, qry=""):
        r = requests.get(self.base_url + '/projects?q=' + qry)

        result = []
        for item in r.json():
            result.append(Project(**item))

        return result

    def workspaces(self):
        r = requests.get(self.base_url + '/workspaces')

        return r.json()

    def providers(self):
        r = requests.get(self.base_url + '/providers')

        return r.json()

    def datasources(self):
        r = requests.get(self.base_url + '/datasources')

        return r.json()

    def jobs(self):
        r = requests.get(self.base_url + '/jobs')

        return r.json()