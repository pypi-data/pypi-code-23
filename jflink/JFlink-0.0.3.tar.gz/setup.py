from setuptools import setup, find_packages

setup(
    name='JFlink',
    package=['JFlink'],
    version='0.0.3',
    description='A collection of tools to improve workflow between JMCT and FISPACT',
    license='MIT License',
    install_requires=['lxml>=4.1.1'],

    author='',
    author_email='',
    url='https://github.com/starmode/JFlink',
    packages=find_packages(),
    platforms='any',
    classifiers=[  
        "Development Status :: 3 - Alpha",  
        "Environment :: Console",  
        "Intended Audience :: Science/Research",  
        "License :: OSI Approved :: MIT License",  
        "Topic :: Scientific/Engineering",  
    ]
)
