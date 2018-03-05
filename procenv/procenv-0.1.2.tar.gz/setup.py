from setuptools import setup

setup(
    name='procenv',
    version='0.1.2',
    description='Run, manage and monitor Procfile-based applications',
    url='https://github.com/sourcelair/procenv',
    author='Paris Kasidiaris',
    author_email='paris@sourcelair.com',
    license='MIT',
    packages=['procenv'],
    install_requires=[
        'honcho>=1.0.0',
        'click>=6.7.0',
    ],
    entry_points={
        'console_scripts': ['procenv=procenv.cli:main'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)
