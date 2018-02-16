from setuptools import setup

import glob

setup(
    name='omegalines',
    version='0.1',
    author='Fabian Peter Hammerle',
    author_email='fabian@hammerle.me',
    url='https://git.hammerle.me/fphammerle/omeglines',
    keywords=['public transportation', 'onion omega'],
    scripts=glob.glob('scripts/*'),
    install_requires=[
        'python-dateutil',
        'pyyaml',
    ],
    # tests_require=['pytest']
)
