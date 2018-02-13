from setuptools import setup

url = 'https://github.com/rendaw/python-trezor-gpg'

setup(
    name='trezor_gpg',
    version='0.0.3',
    author='rendaw',
    author_email='spoo@zarbosoft.com',
    url=url,
    download_url=url + '/tarball/v0.0.1',
    license='BSD',
    description='Use Trezor for GPG passphrases',
    long_description=open('readme.md', 'r').read(),
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
    install_requires=[
        'trezor==0.9.0',
    ],
    py_modules=['trezor_gpg'],
    entry_points={
        'console_scripts': [
            'trezor_gpg = trezor_gpg:main',
        ],
    },
)
