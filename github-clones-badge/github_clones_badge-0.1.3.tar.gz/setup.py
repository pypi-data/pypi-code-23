from setuptools import setup
setup(
  name = 'github_clones_badge',
  packages = ['github_clones_badge'], 
  install_requires=[
   'requests == 2.18.4',
   'python-crontab'
    ],
  data_files=[('data',['github_clones_badge/data/README.md']),
              ('badges',['github_clones_badge/badges/README.md'])
    ],
  include_package_data=True,
  version = '0.1.3',
  description = 'A small package to create badges that count github clones',
  long_description="A python package that automates the pulling of traffic information using the GitHub API, storing this information and creating badges that can be uploaded to the repository's README.md",
  author = 'Alexandar Mechev',
  author_email = 'apmechev@gmail.com',
  url = 'https://github.com/apmechev/github_clones_badge', 
  download_url = 'https://github.com/apmechev/github_clones_badge/archive/v0.1.0.tar.gz',
  keywords = ['github', 'github_badges', 'developer_tools' ], 
  classifiers = ['Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      "License :: OSI Approved :: GNU General Public License v3 (GPLv3)" ,
      "Natural Language :: English",
      "Topic :: Software Development :: Documentation",
      "Topic :: Software Development :: Widget Sets",
      "Topic :: Utilities",
#      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.2',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',],
)

