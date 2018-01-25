"""A paste.script template following gocept Python package conventions."""

from setuptools import setup, find_packages


setup(
    name='gocept.package',
    version='3.0',

    install_requires=[
        'PasteScript',
        'pkginfo>=0.9',
        'setuptools',
    ],

    extras_require={
        'doc': [
            'Sphinx>=1.3',
        ],
        'test': [
            'gocept.testing',
        ],
    },

    entry_points={
        'console_scripts': [
            'doc=gocept.package.doc:main',
        ],
        'paste.paster_create_template': [
            'gocept-package = gocept.package.skeleton:PackageSkeleton',
            'gocept-webapp = gocept.package.skeleton:WebAppDeploymentSkeleton',
        ],
    },

    author='gocept <mail@gocept.com>',
    author_email='mail@gocept.com',
    license='ZPL 2.1',
    url='https://bitbucket.org/gocept/gocept.package/',

    keywords='paste.script paster create template python package sphinx theme'
             'deployment batou webapp',
    classifiers="""\
Environment :: Plugins
Framework :: Paste
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
"""[:-1].split('\n'),
    description=__doc__.strip(),
    long_description='\n\n'.join(open(name).read() for name in (
        'README.rst',
        'HACKING.rst',
        'CHANGES.rst',
    )),

    namespace_packages=['gocept'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
)
