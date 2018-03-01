from setuptools import setup, find_packages

setup(
    name='dimagi-memoized',
    version='1.0.1',
    description="A simple memoization decorator that's also memory efficient on instance methods",
    long_description="",
    url="https://github.com/dimagi/memoized",
    author='Dimagi',
    author_email='dev@dimagi.com',
    license='BSD-3',
    py_modules=['memoized'],
    install_requires=(),
    test_requires=(
        'nose',
    )
)
