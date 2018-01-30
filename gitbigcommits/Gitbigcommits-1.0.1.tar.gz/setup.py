#!/usr/bin/env python

from setuptools import setup
import pkg_resources

setup(name='Gitbigcommits',
      version='1.0.1',
      description='Report for large commits in your git repo',
      author='Viswesh M',
      author_email='mviswesh5@gmail.com',
      packages=['gitbigcommits', 'gitbigcommits.core',
                'gitbigcommits.report_layer', 'gitbigcommits.miscellaneous'],
      license='GNU',
      package_data={'gitbigcommits': ['miscellaneous/*']},
      long_description=open(
          pkg_resources.resource_filename(__name__, "README.txt")).read(),
      entry_points={
          'console_scripts': [
              'bigcommits = gitbigcommits.report_layer.git_html_report:console_output',
              'bigcommits-html = gitbigcommits.report_layer.git_html_report:fat_html_output',
              'dbranch-html = gitbigcommits.report_layer.git_html_report:dorm_branch_html_output'
          ],
      },
      install_requires=[
          "Cheetah3 >= 3.0.0",
      ],
      )
