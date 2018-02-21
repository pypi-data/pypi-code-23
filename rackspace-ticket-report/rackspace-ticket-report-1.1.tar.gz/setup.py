from setuptools import setup


NAME = "Jesse Cook"
EMAIL = "jesse.cook@rackspace.com"

setup(name="rackspace-ticket-report",
      description="Get ticket report from Rackspace Private Cloud Insights",
      long_description=open("README.rst", "r").read(),
      license="Apache Software License",
      version="1.1",
      author=NAME,
      author_email=EMAIL,
      maintainer=NAME,
      maintainer_email=EMAIL,
      scripts=["get_ticket_report.py"],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Apache Software License",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 3"],
      install_requires=["requests>=2.18.0"])
