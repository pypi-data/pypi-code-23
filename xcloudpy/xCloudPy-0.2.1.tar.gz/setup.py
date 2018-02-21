from setuptools import setup, find_packages

setup(
    name='xCloudPy',
    packages=find_packages(exclude=['tests*']),  # this must be the same as the name above
    version='0.2.1',
    description='Public cloud libs basic wrapper',
    author='Arturo Martinez',
    author_email='wankes2000@gmail.com',
    url='https://github.com/wankes2000/xCloudPy',  # use the URL to the github repo
    download_url='https://github.com/wankes2000/xCloudPy/archive/0.2.1.tar.gz',
    install_requires=['boto3==1.5.22', 'google-cloud-datastore==1.4.0', 'google-cloud-storage==1.7.0'],
    tests_require=['mock','nose==1.3.7','coverage==4.0.3', 'localstack==0.8.5'],
    keywords=['aws', 'cloud', 'google', 'gcp'],  # arbitrary keywords
    classifiers=[],
)
