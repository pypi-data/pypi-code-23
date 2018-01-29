from distutils.core import setup

setup(
    name='Marilyn',
    packages=['Marilyn'],  # this must be the same as the name above
    version='0.0.1',
    description='Marilyn SDK',
    author='user',
    author_email='skar404@gmail.com',
    url='https://github.com/peterldowns/mypackage',  # use the URL to the github repo
    download_url='https://github.com/skar404/marilyn/archive/master.zip',  # I'll explain this in a second
    keywords=['marilyn', 'sdk', 'api'],  # arbitrary keywords
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
