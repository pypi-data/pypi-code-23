from setuptools import setup
import os

setup(
    name='cloudtoken-plugin.okta',
    version="0.0.1",
    description='OKTA plugin for cloudtoken.',
    url='https://bitbucket.org/atlassian/cloudtoken',
    author='Andy Loughran',
    author_email='andy@lockran.com',
    license='Apache',
    py_modules=['cloudtoken_plugin.okta'],
    zip_safe=False,
    python_requires='>=3.5',
    install_requires=[
        "cloudtoken>=0.0.1",
        ],
)
