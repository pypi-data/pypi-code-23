import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'marshmallow>=3.0.0b1'
    ]

setup(name='compound-jsonapi',
      version='1.0.0',
      description='Compound JSONAPI document extension for Marshmallow',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        ],
      author='Mark Hall',
      author_email='mark.hall@work.room3b.eu',
      lincense='MIT',
      url='https://bitbucket.org/mhall/compound-jsonapi',
      keywords='',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      test_suite='tests',
      )
