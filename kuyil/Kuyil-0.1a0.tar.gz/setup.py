from setuptools import setup

setup(name = 'Kuyil',
        version='0.1a',
        license='BSD',
        url='https://github.com/4info/Kuyil',
        description='testing sample rsj',
        author='rohitash',
        author_email='rohitash@sigmoid.com',
        packages=['Kuyil',
                'Kuyil.api',
                'Kuyil.dao',
                'Kuyil.db_connection',
                'Kuyil.entity',
                'Kuyil.util',
                'Kuyil.repository_client_factory'],

        install_requires=['SQLAlchemy==1.2.2'],
)

__author__ = 'rohitash'