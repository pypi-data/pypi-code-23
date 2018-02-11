from setuptools import setup, find_packages


setup(
    name='coverage_python_version',
    version='0.1.0',
    description='A coverage.py plugin to facilitate exclusions based on'
    ' Python version',
    long_description=open('README.rst', 'r').read(),
    keywords='coverage plugin version exclude',
    author='Jason Simeone',
    author_email='jay@classless.net',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',
    ],
    url='https://github.com/jayclassless/coverage_python_version',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=True,
    include_package_data=True,
    install_requires=[
        'coverage>=4.5,<5',
    ],
)

