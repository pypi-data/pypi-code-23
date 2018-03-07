#!/usr/bin/env python

from setuptools import setup


entry_points = {
    'console_scripts': [
        'save_repo_state = repo_state.save_repo_state:main',
        'enforce_repo_state = repo_state.enforce_repo_state:main'
    ]
}

setup(name='repo_state',
      version='0.2',
      description='Capture state of multiple git repositories into a json file, and later enforce that state onto a directory',
      author='Jeff Gable',
      author_email='jeff@promenadesoftware.com',
      packages=['repo_state'],
      entry_points=entry_points,
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: POSIX",
          "License :: OSI Approved :: MIT License",
      ]
      )
