import os

from setuptools import setup

readme_file = os.path.join(os.path.dirname(__file__), 'README.rst')
if not os.path.isfile(readme_file):
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_file) as readme:
    README = readme.read()


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-yeouia',
    version='1.1.1',
    packages=['yeouia'],
    install_requires=['Django>=1.11'],
    include_package_data=True,
    license='BSD',
    description='A Django auth backend that works with email or username',
    long_description=README,
    url='https://github.com/nim65s/django-YummyEmailOrUsernameInsensitiveAuth',
    author='Guilhem Saurel',
    author_email='webmaster@saurel.me',
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
