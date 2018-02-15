from setuptools import setup

setup(name='epynet',
      version='1.0',
      description='Vitens EPANET 2.0 wrapper and utilities',
      url='https://github.com/vitens/epynet',
      author='Abel Heinsbroek',
      author_email='abel.heinsbroek@vitens.nl',
      license='Apache Licence 2.0',
      packages=['epynet'],
      install_requires = [
          'pandas'
      ],
      zip_safe=False)
