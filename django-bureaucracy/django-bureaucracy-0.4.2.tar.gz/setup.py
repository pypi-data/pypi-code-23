import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-bureaucracy',
    version='0.4.2',
    packages=['django_bureaucracy'],
    include_package_data=True,
    description='Django layer on top of the bureaucracy package',
    long_description=README,
    install_requires=[
        'django',
        'burocracy>=0.4.1'
    ],
    author='Maykin Media, Robin Ramael, Sergei Maertens',
    author_email='robin.ramael@maykinmedia.nl,sergei@maykinmedia.nl',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
