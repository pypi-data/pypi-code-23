from setuptools import setup

setup(
    name='Henosis',
    packages=['Henosis'],
    version='0.0.1',
    description='A Python 3 implementation of LoOP: Local Outlier Probabilities, a local density based outlier detection method providing an outlier score in the range of [0,1].',
    author='Valentino Constantinou',
    author_email='vc@valentino.io',
    url='https://github.com/vc1492a/henosis',
    download_url='https://github.com/vc1492a/henosis/archive/0.0.1.tar.gz',
    keywords=['recommendation', 'system', 'predictive', 'machine', 'learning', 'modeling', 'recommender'],
    classifiers=[],
    license='Apache License, Version 2.0',
    install_requires=[
        'boto3',
        'dill',
        'Flask',
        'Flask-CORS',
        'Flask-HTTPAuth',
        'Flask-RESTful',
        'gevent',
        'imbalanced-learn',
        'Jinja2',
        'jwt',
        'numpy',
        'pandas',
        'pyldap',
        'pymssql',
        'PyYAML',
        'requests',
        'scikit-learn'
    ]
)
