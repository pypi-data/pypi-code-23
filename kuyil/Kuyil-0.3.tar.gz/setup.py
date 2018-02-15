from setuptools import setup

setup(name = 'Kuyil',
        version='0.3',
        license='BSD',
        url='https://github.com/4info/Kuyil',
        description='sprint 1 rc',
        author='rohitash',
        author_email='rohitash@sigmoid.com',
        packages=['Kuyil',
                'Kuyil.api',
                'Kuyil.models',
                'Kuyil.utils',
                'Kuyil.repository_client',
                'tests'],

        install_requires=['SQLAlchemy==1.2.2',
                          'SQLAlchemy-Utils == 0.32.21',
                          'boto3 == 1.5.22',
                          'pytest-cov == 2.5.1',
                          'MySQL-python==1.2.5'
                          ],
)

__author__ = 'rohitash'