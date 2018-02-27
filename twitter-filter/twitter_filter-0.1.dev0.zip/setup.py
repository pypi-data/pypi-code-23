from setuptools import setup, find_packages

setup(
    name='twitter_filter',
    version='0.1dev',
    packages=find_packages(exclude=['tests*']),
    url='https://github.com/abdulrahimGhazal/twitter_filter',
    license='MIT',
    description='Twitter Live Data Collector',
    author='AbdulrahimGhazal',
    author_email='abdulrahim.ghazal.1994@gmail.com',
    long_description=open('README.txt').read(),
)
