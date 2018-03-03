from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='opengrokfs',
    description='OpenGrok FUSE filesystem and tools',
    long_description=readme(),
    license='MIT',
    url='https://github.com/rabinv/opengrokfs',
    author='Rabin Vincent',
    author_email='rabin@rab.in',
    version='0.2.1',
    install_requires=[
        'attrs>=16.3.0',
        'dateparser>=0.6.0',
        'fusepy>=2.0.4',
        'lxml>=3.7.1',
        'requests>=2.12.4',
        'requests_cache>=0.4.13',
    ],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'opengrokfs = opengrokfs.opengrokfs:main',
            'oggrep = opengrokfs.grep:main',
            'ogcscope = opengrokfs.cscope:main'
        ],
    },
    packages=['opengrokfs'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
)
