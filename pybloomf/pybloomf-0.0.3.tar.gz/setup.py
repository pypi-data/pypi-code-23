from setuptools import setup

setup(
    name='pybloomf',
    version='0.0.3',
    description='Python implementation of Bloom filter algorithm',
    url='https://github.com/tomasrasymas/pybloomf',
    author='Tomas Rasymas',
    author_email='tomas.rasymas@gmail.com',
    license='MIT',
    data_files=[('', ['LICENSE'])],
    install_requires=[
        'bitarray>=0.8.1',
        'mmh3>=2.5.1',
    ],
    test_suite='tests',
    packages=['pybloomf']
)