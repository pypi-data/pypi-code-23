from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''


install_requires=[
    "configparser",
    'requests',
    'six'
]

testpkgs = [
    "nose==1.3.7",
    "coverage",
    "mock"
]
setup(description='This is the official Python SDK for Contacthub REST API. This SDK easily allows to access your data '
                  'on Contacthub, making the authentication immediate and simplifying read/write operations.',
      author='Contactlab',
      url='https://github.com/contactlab/contacthub-sdk-python',
      version='0.2',
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Intended Audience :: Customer Service',
                   'Intended Audience :: Developers',
                   'Development Status :: 5 - Production/Stable'
                   ],
      keywords='web skd api',
      author_email='developer@contactlab.com',
      install_requires=install_requires,
      packages=find_packages(exclude=['tests', 'tests.*']),
      extras_require={
          'testing': testpkgs,
          'documentation': ['Sphinx==1.4.1', 'sphinx_rtd_theme']
      },
      scripts=[],
      name='contacthub-sdk-python',
      long_description=README,
      include_package_data=False,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=testpkgs,
      )
