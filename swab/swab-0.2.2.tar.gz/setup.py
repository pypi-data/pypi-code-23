from setuptools import setup
import os
import re


VERSIONFILE = "swab/__init__.py"


def get_version():
    return re.search("^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                     read(VERSIONFILE), re.M).group(1)


def read(*path):
    """
    Return content from ``path`` as a string
    """
    with open(os.path.join(os.path.dirname(__file__), *path), 'rb') as f:
        return f.read().decode('UTF-8')


setup(
    name='swab',
    version=get_version(),
    description="Swab: Simple WSGI A/B testing",
    long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    keywords='ab, a/b, a/bingo, split testing',
    author='Oliver Cope',
    author_email='oliver@redgecko.org',
    url='https://ollycope.com/software/swab/',
    license='BSD',
    packages=['swab'],
    include_package_data=True,
    package_data={'': ['static/*', 'templates/*']},
    zip_safe=False,
    install_requires=['fresco',
                      'fresco-static',
                      'fresco-template',
                      'piglet-templates',
                      ],
    entry_points="""
    """,
    dependency_links=[]
)
