from setuptools import setup

setup(
    name='IOSStickersExtension',
    packages=['IOSStickersExtension'],
    package_dir={'': 'src'},
    version='1.9',
    description='',
    author='Ron Eskogido',
    author_email='rona@tabtale.com',
    url='https://github.com/TabTale/iOSStickersExtension',
    # download_url='https://github.com/peterldowns/mypackage/archive/0.1.tar.gz',
    include_package_data=True,
    keywords=[],
    classifiers=[],
    install_requires=[
        'pillow'
    ]
)
