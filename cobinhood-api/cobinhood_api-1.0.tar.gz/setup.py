from setuptools import setup
setup(
    name = 'cobinhood_api',
    packages = ['cobinhood_api'],
    version = '1.0',
    description = 'API wrapper for Cobinhood exchange written in Python',
    long_description = 'API wrapper for Cobinhood exchange written in Python',
    author = 'Thomas Beukema',
    author_email = 'thomas@thomasbeukema.me',
    url = 'https://github.com/thomasbeukema/cobinhood_api',
    download_url = 'https://github.com/thomasbeukema/cobinhood_api/archive/1.0.tar.gz',
    keywords = ['cobinhood', 'api', 'crypto', 'exchange'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers'
    ],
    python_requires = '>=3',
    license='MIT',
    project_urls={
        'Documentation': 'https://github.com/thomasbeukema/cobinhood_api',
        'Funding': 'https://github.com/thomasbeukema/cobinhood_api',
        'Source': 'https://github.com/thomasbeukema/cobinhood_api',
        'tracker': 'https://github.com/thomasbeukema/cobinhood_api/issues'
    }
)
