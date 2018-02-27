try:
    from setuptools import setup
except ImportError as _:
    from distutils.core import setup
from airship_python.version import VERSION


setup(
    name='airship-python',
    packages=['airship_python'],
    version=VERSION,
    description='Airship Python SDK',
    author='Airship Support',
    author_email='support@airshiphq.com',
    license='MIT',
    url='https://github.com/airshiphq/airship-python',
    keywords=['feature', 'flag', 'airship'],
    install_requires=[
        'requests>=2.18.4',
        'jsonschema>=2.6.0',
        'python-dateutil>=2.6.1'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ],
)
