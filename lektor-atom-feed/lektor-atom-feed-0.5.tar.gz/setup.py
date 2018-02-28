from setuptools import setup

setup(
    name='lektor-atom-feed',
    version='0.5',
    author=u'A. Jesse Jiryu Davis',
    author_email='jesse@emptysquare.net',
    license='MIT',
    py_modules=['lektor_atom'],
    install_requires=['MarkupSafe'],
    tests_require=['lxml', 'pytest'],
    url='https://github.com/VaultVulp/lektor-atom',
    entry_points={
        'lektor.plugins': [
            'atom-feed = lektor_atom:AtomPlugin',
        ]
    }
)
