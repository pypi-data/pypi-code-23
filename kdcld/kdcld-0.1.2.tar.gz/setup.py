from setuptools import setup, find_packages

version = '0.1.2'

setup(
    name='kdcld',
    version=version,
    description='命令行词典',
    classifiers=[],
    packages=find_packages(),
    url='',
    license='',
    author='kindan',
    author_email='kind4n@gmail.com',
    include_package_data=True,
    install_requres=[
        'bs4',
        'requests',
        'termcolor'
    ],
    entry_points={
        'console_scripts': [
            'search = kdcld.cld:main'
        ]
    }
)
