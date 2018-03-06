from distutils.core import setup


setup(
    name='airship-python',
    packages=['airship_python'],
    version='1.1.4',
    description='Airship Python SDK',
    long_description='Airship Python SDK',
    author='Airship Support',
    author_email='support@airshiphq.com',
    license='MIT',
    url='https://github.com/airshiphq/airship-python',
    keywords=['feature', 'flag', 'airship'],
    install_requires=[
        'requests>=2.18.4',
        'jsonschema>=2.6.0',
        'python-dateutil>=2.6.1',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    python_requires='>=2.6, <3',
)
