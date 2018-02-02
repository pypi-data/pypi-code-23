from setuptools import setup

from paypro.version import VERSION

setup(
    name='paypro',
    version=VERSION,
    author='PayPro',
    author_email='development@paypro.nl',
    description='Client for PayPro API v1',
    url='https://github.com/paypronl/paypro-python-v1',
    license='MIT',
    keywords=['paypro', 'payment', 'service'],
    install_requires=[
        'requests'
    ],
    packages=['paypro'],
    package_data={'paypro': ['data/ca-bundle.crt']},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)