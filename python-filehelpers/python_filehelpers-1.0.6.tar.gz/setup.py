from setuptools import setup

VERSION = __import__("filehelpers").__version__

setup(
    name='python_filehelpers',
    description='A set of various file helpers.',
    version=VERSION,
    license='MIT',
    author='Dusty Gamble',
    author_email='dusty.gamble@gmail.com',
    url='https://github.com/ipsod/python_filehelpers',
    packages=['filehelpers'],
    zip_safe=False,
    classifiers=[
        'Topic :: Utilities',
        'Topic :: Text Processing',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        # 'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ]
)
