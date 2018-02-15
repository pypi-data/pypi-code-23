from setuptools import setup

setup(
    python_requires='>3.5.1',
    name='glacier-backup-sync',
    version='1.2.3',
    description='''This package provides the command "glacier_sync".
        It enabled you to a) rotate your backups on a weekly basis and b) synchronize your weekly
        backups to Amazon Glacier.''',
    author='Stefan Schärmeli',
    author_email='schaermu@smartfactory.ch',
    url='https://git.smartfactory.ch/smartfactory-public/python-glacier-sync',
    download_url='''https://git.smartfactory.ch/smartfactory-public/python-glacier-sync/repository/
        archive.tar.gz?ref=v1.2.3''',
    keywords=['backup', 'glacier', 'cli'],
    py_modules=['sync'],
    packages=['classes'],
    install_requires=[
        'boto3==1.5.28',
        'colorama<=0.3.7',
        'Click',
        'awscli==1.14.38'
    ],
    entry_points='''
        [console_scripts]
        glacier_sync=sync:cli
    ''',
)
