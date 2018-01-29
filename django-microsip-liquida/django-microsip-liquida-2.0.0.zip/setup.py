import os,sys, compileall
from setuptools import setup,find_packages

# README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
if "sdist" in sys.argv:
    path = os.path.abspath(os.path.dirname(__file__))+"\\django_microsip_base\\"
    compileall.compile_dir(path, force=True)

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-microsip-liquida',
    version = '2.0.0',
    packages = find_packages(),
    include_package_data = True,
    license = 'BSD License', # example license
    description = 'Enlace Liquidacion Microsip',
    long_description = 'README',
    url = 'http://www.example.com/',
    author = 'Servicios de Ingenieria Computacional',
    author_email = 'desarrollo@siccomputacion.com',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
