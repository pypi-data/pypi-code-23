# coding: utf-8
from setuptools import setup, find_packages

import pg_lock_monitor

setup(
    name='pg_lock_monitor',
    version=pg_lock_monitor.__version__,
    author='Ruslan Gilfanov',
    author_email='rg@informpartner.com',
    packages=find_packages(),
    package_dir={'pg_lock_monitor': 'pg_lock_monitor'},
    package_data={
        'pg_lock_monitor': ['sql/*']
    },
    install_requires=[
        'psycopg2',
        'pytz',
        'python-telegram-bot',
    ],
    entry_points={
        'console_scripts': [
            'pg_lock_monitor = pg_lock_monitor.pg_lock_monitor:main',
        ]
    },
)
