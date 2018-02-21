from setuptools import setup, find_packages

from pypack.package import (
    NAME,
    VERSION,
    LICENSE,
    URL,
    DESCRIPTION,
    AUTHOR,
    EMAIL,
    PACKAGE,
    LIBRARY,
    KEYWORDS
)

setup (
    name = NAME,
    version = VERSION,
    url = URL,
    description = DESCRIPTION,
    long_description = '',
    author = AUTHOR,
    author_email = EMAIL,
    license = LICENSE,
    classifiers=[

    ],
    keywords=KEYWORDS,
    packages= ['{0}/{1}'.format(PACKAGE,LIBRARY)], #find_packages(exclude=['contrib', 'docs', 'tests*']),
    data_files=[],
    install_requires=[],
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            'pypack = pypack.pypack_cli:main',
        ],
    },

)
