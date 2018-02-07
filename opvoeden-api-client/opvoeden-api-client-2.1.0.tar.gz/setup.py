import io

from setuptools import find_packages, setup

setup(
    name='opvoeden-api-client',
    version='2.1.0',
    description='Client for Stichting Opvoeden API V2',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    keywords=['stichting', 'opvoeden', 'api', 'client', 'rest'],
    author='Jaap Roes (Leukeleu)',
    author_email='jroes@leukeleu.nl',
    maintainer='Leukeleu',
    maintainer_email='info@leukeleu.nl',
    url='https://github.com/leukeleu/opvoeden-api-client',
    packages=find_packages(exclude=['tests']),
    install_requires=['requests'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    license='MIT',
    test_suite='tests',
    include_package_data=True,
    zip_safe=False
)
