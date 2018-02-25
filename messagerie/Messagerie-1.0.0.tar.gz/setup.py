from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='Messagerie',
      version='1.0.0',
      description='Custom wrapper to aws services',
      long_description=readme(),
      url='https://github.com/stikks/messagerie',
      author='stikks',
      author_email='styccs@gmail.com',
      maintainer='stikks',
      maintainer_email='styccs@gmail.com',
      include_package_data=True,
      keywords='aws, python, boto3',
      license='MIT',
      packages=['messagerie'],
      install_requires=[
          'requests',
          'boto3',
          'pyshorteners'
      ])
