from setuptools import setup

setup(name='phreeqpython',
      version='1.2',
      description='Vitens PHREEQC wrapper and utilities',
      url='https://github.com/Vitens/phreeqpython',
      author='Abel Heinsbroek',
      author_email='abel.heinsbroek@vitens.nl',
      license='Apache Licence 2.0',
      packages=['phreeqpython'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['periodictable']
      )
