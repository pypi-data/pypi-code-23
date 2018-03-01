# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='PyPiwi',
      version=open('VERSION').read().strip(),
      packages=['pypiwi'],
      url='https://bitbucket.org/creeerio/pypiwi',

      author='Nils',
      author_email='nils@creeer.io',
      license='MIT',

      description='Piwi; Peewee, more.',

      classifiers=[
          # 3 - Alpha, 4 - Beta, 5 - Production/Stable
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
      ],

      install_requires=['peewee', 'inflection'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'])
