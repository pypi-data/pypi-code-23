from setuptools import setup

setup(
    name='cmctl',
    packages=['cmctl'],
    version='1.0.1',
    description='Conductometer Control Tool',
    url='https://github.com/hubpav/cmctl',
    author='Pavel Hubner',
    author_email='pavel.hubner@gmail.com',
    license='MIT',
    keywords = ['conductometer', 'cli', 'tool'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Environment :: Console',
        'Intended Audience :: Science/Research'
    ],
    install_requires=[
        'click==6.7', 'pyserial==3.4'
    ],
    entry_points='''
        [console_scripts]
        cmctl=cmctl.cli:main
    '''
)
