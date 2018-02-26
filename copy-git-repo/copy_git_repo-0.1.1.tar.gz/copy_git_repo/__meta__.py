
__name__ = 'copy_git_repo'
name_url = __name__.replace('_', '-')

__version__ = '0.1.1'
__description__ = 'Copy repo excluding files mentionned in .gitignore'
__long_description__ = 'See repo README'
__author__ = 'oscar6echo'
__author_email__ = 'olivier.borderies@gmail.com'
__url__ = 'https://github.com/{}/{}'.format(__author__,
                                            name_url)
__download_url__ = 'https://github.com/{}/{}/tarball/{}'.format(__author__,
                                                                name_url,
                                                                __version__)
__keywords__ = ['copy', 'git', 'repo', 'shutil']
__license__ = 'MIT'
__classifiers__ = ['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6'
                   ]
__include_package_data__ = True
__package_data__ = {}
__zip_safe__ = False
__entry_points__ = {
    'console_scripts': [
        'copy-repo = copy_git_repo.cli:main',
    ]
}
