from setuptools import setup, find_packages

setup(name = 'Kuyil',
        version='0.5',
        license='BSD',
        url='https://github.com/4info/Kuyil',
        description='sprint 1 rc',
        author='rohitash',
        author_email='rohitash@sigmoid.com',
        packages=find_packages(),
        package_data={'': ['config.json']},
        data_files=[('.', ['config.json'])],
        include_package_data=True,

        install_requires=['SQLAlchemy==1.2.2',
                          'SQLAlchemy-Utils == 0.32.21',
                          'boto3 == 1.5.22',
                          'pytest-cov == 2.5.1',
                          'MySQL-python==1.2.5'
                          ],
)

__author__ = 'rohitash'