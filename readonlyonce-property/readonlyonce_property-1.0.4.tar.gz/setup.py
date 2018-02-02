from setuptools import setup

setup(
    name='readonlyonce_property',
    version='1.0.4',
    license='Apache 2.0',
    description='@readonlyonce_property decorator that cache its return value.',
    author='Daniel Hilst Selli <danielhilst@gmail.com>',
    url='https://github.com/dhilst/readonlyonce_property',
    py_modules=['readonlyonce_property'],
    test_suite='readonlyonce_property.test',
)
