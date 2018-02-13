import os
from setuptools import find_packages, setup

import djabberd

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    readme_lines = readme.readlines()
description = readme_lines[0].strip()
README = ''.join(readme_lines)


setup(
    name='djabberd',
    version=djabberd.__version__,
    include_package_data=not False,
    packages=find_packages(),
    license='GPL v3',
    description=description,
    long_description=README,
    author='Alexandre Varas',
    author_email='alej0varas@gmail.com',
    url='https://github.com/alej0varas/djabberd',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=1.8,<2',
        'djangorestframework>=3.2,<4',
    ],
)
