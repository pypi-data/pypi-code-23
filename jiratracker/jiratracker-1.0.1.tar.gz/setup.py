#!/usr/bin/env python

from setuptools import setup

setup(name='jiratracker',
      version='1.0.1',
      description='Automatically logs development time to Jira based on Git checkout history',
      long_description='Automatically logs development time to Jira based on Git checkout history. See the documentation at https://github.com/dor-denis/JiraTracker',
      author='Denys Dorofeiev',
      author_email='dor.denis.de@gmail.com',
      url='https://github.com/dor-denis/JiraTracker',
      packages=['JiraTracker'],
      install_requires=[
          'requests',
          'pyyaml'
      ],
      keywords="jira log track"
      )
