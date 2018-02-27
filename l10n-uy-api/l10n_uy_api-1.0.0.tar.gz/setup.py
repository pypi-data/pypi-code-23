from setuptools import setup, find_packages
from codecs import open
from os import path

setup(
    name='l10n_uy_api',
    version='1.0.0',
    description='Libreria para localizacion Uruguaya',
    long_description='Libreria para localizacion Uruguaya',
    url='',
    author='BLUEORANGE GROUP',
    author_email='daniel@blueorange.com.ar',
    license='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='Libreria para localizacion Uruguaya',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'zeep',
        'python-dateutil',
        'M2Crypto',
        'pytz',
        'unidecode',
        'BeautifulSoup'
    ],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
)
