from setuptools import setup, find_packages

setup(name='cargo-simplequery',
      version='0.2',
      description='Wrapper around psycopg2 to build SQL queries',
      url='https://gitlab.cargo.one/abc',
      author='Mike Roetgers',
      author_email='mr@cargo.one',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)
