try:
    from setuptools import setup
except ImportError:
    from distutils import setup

readme = open('README.rst', 'r')
README_TEXT = readme.read()
readme.close()

setup(
    name='aniso8601',
    version='2.0.1',
    description='A library for parsing ISO 8601 strings.',
    long_description=README_TEXT,
    author='Brandon Nielsen',
    author_email='nielsenb@jetfuse.net',
    url='https://bitbucket.org/nielsenb/aniso8601',
    extras_require={'relative': ['python-dateutil']},
    packages=['aniso8601'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='iso8601 parser',
    project_urls={
        'Documentation': 'http://aniso8601.readthedocs.io/en/latest/',
        'Source': 'https://bitbucket.org/nielsenb/aniso8601',
        'Tracker': 'https://bitbucket.org/nielsenb/aniso8601/issues'
    }
)
