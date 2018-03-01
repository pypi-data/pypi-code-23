from setuptools import setup, find_packages

setup(name='cargo-simplequery',
      version='0.2.1',
      description='Wrapper around psycopg2 to build SQL queries',
      url='https://gitlab.cargo.one/python/cargo-simplequery',
      author='Mike Roetgers',
      author_email='mr@cargo.one',
      license='MIT',
      install_requires=['psycopg2>=2.7.3.2'],
      packages=find_packages(),
      zip_safe=False)
