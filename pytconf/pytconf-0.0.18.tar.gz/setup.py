import setuptools

"""
The documentation can be found at:
http://setuptools.readthedocs.io/en/latest/setuptools.html
"""
setuptools.setup(
    # the first three fields are a must according to the documentation
    name='pytconf',
    version='0.0.18',
    packages=[
        'pytconf',
    ],
    # from here all is optional
    description='pytconf handles configuration, config files and command line parsing',
    long_description='pytconf handles configuration, config files and command line parsing',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    maintainer='Mark Veltzer',
    maintainer_email='mark.veltzer@gmail.com',
    keywords=[
        'click',
        'argparse',
        'optparse',
        'command-line-parser',
        'configuration',
    ],
    url='https://veltzer.github.io/pytconf',
    download_url='https://github.com/veltzer/pytconf',
    license='MIT',
    platforms=[
        'python2',
    ],
    install_requires=[
        'enum34',
        'termcolor',
        'six',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    data_files=[
    ],
    entry_points={'console_scripts': [
    ]},
    python_requires='>=2.7',
)
