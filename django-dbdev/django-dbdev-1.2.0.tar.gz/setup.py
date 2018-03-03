import json
import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'django_dbdev', 'version.json')) as f:
    version = json.loads(f.read())


long_description = """
Do you want to make it easy to create and setup isolated
Postgres or MySQL database servers during development
of your Django project?

See https://github.com/espenak/django_dbdev
"""

setup(
    name='django-dbdev',
    description='Makes it easy to create and manage databases during development.',
    license='BSD',
    version=version,
    url='http://github.com/appressoas/django_dbdev',
    author='Espen Angell Kristiansen',
    author_email='post@espenak.net',
    long_description=long_description,
    packages=find_packages(exclude=['dbdev_testproject']),
    install_requires=[
        'Django>=1.10',
        'sh',
        'future'
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
