from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='languagepy',
    version='0.1',
    description='Write Python in your native language and transpile it to standard Python',
    long_description=readme(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Text Processing :: Linguistic',
    ],
    project_urls={
        'Website': 'https://languagepy.org',
        'Documentation': 'https://docs.languagepy.org',
        'Source': 'https://github.com/caveljan/languagepy/',
        'Tracker': 'https://github.com/caveljan/languagepy/issues',
    },
    keywords='python native language',
    url='https://languagepy.org',
    author='Jan Cavel',
    author_email='mail@caveljan.com',
    license='MIT',
    packages=['languagepy'],
    entry_points = {
        'console_scripts': ['languagepy=languagepy.command_line:main'],
    },
    python_requires='>=3',
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    zip_safe=False)
