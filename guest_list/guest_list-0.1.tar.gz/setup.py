from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='guest_list',
      version='0.1',
      description='Simple python package for a company to generate a guest ' +
                  'list from a data file containing json encoded customer ' +
                  'coordinates, based on their distance to the ' +
                  'companies office.',
      long_description=readme(),
      url='https://github.com/kujosHeist/guest_list',
      author='Shane Carty',
      author_email='shane.carty@hotmail.com',
      license='MIT',
      packages=['guest_list'],
      install_requires=[
        'geopy'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
