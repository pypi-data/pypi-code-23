
__name__ = 'sgmarkets_api_auth'
name_url = __name__.replace('_', '-')

__packages__ = [__name__]
__version__ = '0.2.0'
__description__ = 'sgmarket api authentication'
__long_description__ = 'See repo README'
__author__ = 'sgmarkets'
__author_email__ = 'olivier.borderies@gmail.com'
__url__ = 'https://gitlab.com/{}/{}'.format(__author__,
                                            name_url)
__download_url__ = 'https://gitlab.com/{}/{}/repository/archive.tar.gz?ref={}'.format(__author__,
                                                                                      name_url,
                                                                                      __version__)
__keywords__ = ['sgmarkets', 'api', 'authentication']
__license__ = 'MIT'
__classifiers__ = ['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6'
                   ]
__include_package_data__ = True
__package_data__ = {
    'img':
        ['img/sg-research-logo-displayed.png',
         ],
    'sample':
        ['sample/my_secret.txt',
         ],
}
__zip_safe__ = False

