from setuptools import setup


NAME = "Brian Curtin"
EMAIL = "brian.curtin@rackspace.com"

setup(name="rackspace-token-generator",
      description="A script to generate Rackspace Cloud Identity tokens",
      long_description=open("README.rst", "r").read(),
      license="Apache Software License",
      version="1.5",
      author=NAME,
      author_email=EMAIL,
      maintainer=NAME,
      maintainer_email=EMAIL,
      scripts=["get_token.py"],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Apache Software License",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 3"],
      install_requires=["keystoneauth1>=3.3.0",
                        "rackspaceauth>=0.6.0"])
