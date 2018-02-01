#!/usr/bin/env python

from setuptools import setup
import pkg_resources

setup(name='Gitbigcommits',
      version='1.0.3',
      description='Reporting tool for large commits happened in your git repo',
      author='Viswesh M',
      author_email='mviswesh5@gmail.com',
      packages=['gitbigcommits', 'gitbigcommits.core',
                'gitbigcommits.report_layer', 'gitbigcommits.miscellaneous',
                'gitbigcommits.prevent_commits'],
      license='GNU',
      package_data={'gitbigcommits': ['miscellaneous/*', 'prevent_commits/*']},
      long_description=open(
          pkg_resources.resource_filename(__name__, "README.txt")).read(),
      entry_points={
          'console_scripts': [
              'bigcommits = gitbigcommits.report_layer.git_html_report:console_output',
              'bigcommits-html = gitbigcommits.report_layer.git_html_report:fat_html_output',
              'dbranch-html = '
              'gitbigcommits.report_layer.git_html_report:dorm_branch_html_output',
              'bigcommits-prevent = '
              'gitbigcommits.prevent_commits.main:install_script'
          ],
      },
      install_requires=[
          "Cheetah3 >= 3.0.0",
      ],
      )
