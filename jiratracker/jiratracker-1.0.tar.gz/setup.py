#!/usr/bin/env python

from setuptools import setup

setup(name='jiratracker',
      version='1.0',
      description='Automatically logs development time to Jira based on Git checkout history',
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
