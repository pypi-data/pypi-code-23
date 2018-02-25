import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djangoplus',
    version='0.0.41',
    packages=find_packages(),
    install_requires=['Django==1.11', 'pycrypto==2.6.1', 'python-dateutil==2.5.3', 'gunicorn==19.5.0', 'selenium==2.53.2', 'xlwt==1.0.0', 'xlrd==0.9.4', 'unicodecsv==0.14.1', 'dropbox==6.5.0', 'html5lib==1.0b8', 'Pillow==3.2.0', 'xhtml2pdf==0.0.6', 'Fabric==1.14.0'],
    scripts=['djangoplus/bin/startproject', 'djangoplus/bin/runserver', 'djangoplus/bin/sync'],
    include_package_data=True,
    license='BSD License',
    description='Metadata-based web framework for the development of management information systems',
    long_description=README,
    url='http://djangoplus.net/',
    author='Breno Silva',
    author_email='brenokcc@yahoo.com.br',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
