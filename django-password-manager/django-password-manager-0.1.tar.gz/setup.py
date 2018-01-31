from distutils.core import setup

from setuptools import find_packages

setup(
    name='django-password-manager',
    version='0.1',
    description='Enable Password Force Reset & Maintain Password History',
    author='Neeraj Dhiman',
    author_email='ndhiman08@gmail.com',
    license='GPL',
    url='https://github.com/inforian/django-password-manager',
    download_url='https://github.com/inforian/django-password-manager/archive/v0.1.tar.gz',
    keywords=['password', 'django-password', 'django-password-manager', 'django-password-manage'],
    classifiers=[],
    packages=find_packages(),
    install_requires=[
        'Django>=1.9',
    ]
)
