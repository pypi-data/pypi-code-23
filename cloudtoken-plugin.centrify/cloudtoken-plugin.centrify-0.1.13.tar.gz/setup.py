from setuptools import setup
import os

version = os.environ['VERSION']

setup(
    name='cloudtoken-plugin.centrify',
    version=version,
    description='Centrify plugin for Cloudtoken.',
    url='https://bitbucket.org/atlassian/cloudtoken',
    author='Atlassian Cloud Engineering',
    author_email='cloud-team@atlassian.com',
    license='Apache',
    py_modules=['cloudtoken_plugin.centrify'],
    zip_safe=False,
    python_requires='>=3.5',
    install_requires=[
        "cloudtoken>=0.1.12",
        "pyquery>=1.3.0",
        "requests>=2.9.1",
        ],
)
