from setuptools import setup, find_packages
from platform import python_version_tuple


def requirements():

    with open('requirements.txt', 'r') as fileobj:
        requirements = [line.strip() for line in fileobj]
        return requirements


def long_description():
    long_dsc = "A library use to run task with multiple threads.\nIf your device have more than one core, it can use full of your cores, so you can focus on your business logic."
    return long_dsc


setup(
    name='MultiThreadTask',
    version='0.0.1',
    url='https://github.com/wangongyouxia/MultiThreadTask',
    license='MIT',
    author='wangongyouxia',
    author_email='709865788@qq.com',
    description='multi-thread-library',
    long_description=long_description(),
    packages=find_packages(),
    install_requires=requirements()
)
