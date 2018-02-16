from setuptools import setup

setup(
    name='ostd',
    version='1.0.1',

    description='Downloads subtitles from OpenSubtitles',
    author='Philipp Ploder',
    url='https://github.com/Fylipp/ostd',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords='opensubtitles',

    packages=['ostd'],

    install_requires=[
        'chardet'
    ]
)
