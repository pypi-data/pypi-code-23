from setuptools import setup
setup(
    name='pyconnectedcars',
    version='0.1.4',
    packages=['pyconnectedcars'],
    include_package_data=True,
    python_requires='>=3',
    install_requires=[
        'python-dateutil',
    ],
    license='MIT',
    description='A library to work with Connected Cars API.',
    long_description='A library to work with Connected Cars car API.',
    url='https://github.com/DarkFox/pyconnectedcars',
    author='Martin Eberhardt',
    author_email='martin@darkfox.dk',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
    ],
)
