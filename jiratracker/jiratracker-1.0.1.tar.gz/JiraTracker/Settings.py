import yaml
import os
from . import Project

class Settings(object):
    def __init__(self, settings_path):
        if not os.path.isfile(settings_path):
            raise FileNotFoundError
        with open(settings_path) as f:
            self.settings = yaml.load(f.read())

    def get_projects(self):
        if 'projects' not in self.settings:
            raise Exceptions.SettingsException('Please specify "projects" in config file')

        projects = []
        overall_hours = self.settings['hours']
        hours = overall_hours / len(self.settings['projects'])
        for project in self.settings['projects']:
            if 'jira_name' not in project:
                raise Exceptions.SettingsException('Please specify "jira_name" in project configuration')
            if 'path' not in project:
                raise Exceptions.SettingsException('Please specify "path" in project configuration')
            if 'jira_url' not in project:
                raise Exceptions.SettingsException('Please specify "jira_url" in project configuration')
            if 'username' not in project:
                raise Exceptions.SettingsException('Please specify "username" in project configuration')
            if 'password' not in project:
                raise Exceptions.SettingsException('Please specify "password" in project configuration')

            projects.append(Project(
                project['jira_name'],
                project['path'],
                project['jira_url'],
                project['username'],
                project['password'],
                hours)
            )

        return projects
