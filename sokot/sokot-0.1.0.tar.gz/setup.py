from setuptools import setup

SHORT_DESCRIPTION = """
A tool to get your member's overtime from King of Time for every N weeks.""".strip()

DEPENDENCIES = [
    'fire',
]

TEST_DEPENDENCIES = [
]

VERSION = '0.1.0'
URL = 'https://github.com/showwin/scrum-overtime-kot'

setup(
    name='sokot',
    version=VERSION,
    description=SHORT_DESCRIPTION,
    url=URL,

    author='showwin',
    author_email='showwin_kmc@yahoo.co.jp',
    license='Apache Software License',

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    entry_points={
        'console_scripts': 'sokot = sokot.main:main'
    },

    keywords='overtime king-of-time scrum python tool cli',

    packages=['sokot'],

    install_requires=DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
)
