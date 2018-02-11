from setuptools import setup, find_packages

setup(
    name='ubm',
    packages=find_packages(),
    version='v1.0.4',
    description='Library for UniBo Motorsport data analysis',
    author='Aaron Russo',
    author_email='axolo6@gmail.com',
    url='https://github.com/Ax6/ubm-python-libraries',
    download_url='https://github.com/Ax6/ubm-python-libraries/archive/v1.0.4.tar.gz',
    classifiers=[],
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'tables'
    ],
)
