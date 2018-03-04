from distutils.core import setup
from setuptools import setup

setup(
    name='Comrade',
    version='0.0.3',
    packages=['comrade'],
    license='MIT',
    entry_points={
        'console_scripts': ['comrade=comrade.command_line:main'],
    },
    author='Erik Hauck',
    description="configurable command line tool",
    url='https://github.com/erikmhauck/comrade',
    install_requires=[
        'menu',
        'future'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'coveralls'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='command line wrapper configurable tool',
    project_urls={
        'Documentation': 'https://github.com/erikmhauck/comrade',
        'Source': 'https://github.com/erikmhauck/comrade',
        'Tracker': 'https://github.com/erikmhauck/comrade/issues',
    },
    python_requires='>=2.7, <4',
    package_data={
        'comrade': ['configs/test_config.json'],
        'comrade': ['configs/sample_config.json'],
    },
)
