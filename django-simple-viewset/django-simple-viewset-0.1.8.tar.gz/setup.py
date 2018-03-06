import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-simple-viewset',
    version='0.1.8',
    description="""Simple viewset for models CRUD operations""",
    long_description=README,
    author='Alejandro Sánchez',
    author_email='elcone@gmail.com',
    url='https://gitlab.com/elcone/django-simple-viewset.git',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    license="MIT",
    zip_safe=False,
    keywords='django,simple,viewset,crud',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
