from distutils.core import setup

version = 1.6

setup(
    name = "byuoauth",
    packages = ["byuoauth"],
    version = version,
    description = "Scripts to easily allow BYU applications to generate OAuth tokens and JWTs for test use.",
    author = "Eric Romrell",
    author_email = "eric_romrell@byu.edu",
    url = "https://github.com/byu-oit/python-token-scripts",
    download_url = "https://github.com/byu-oit/python-token-scripts/archive/{}.tar.gz".format(version),
    keywords = ["byu", "oauth", "token", "jwt"],
    classifiers = [],
    requires = ['requests']
)
