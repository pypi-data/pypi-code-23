
try:
    from setuptools import setup
except:
    from distutils.core import setup
NAME = "waiterdb"
PACKAGES = ["waiterdb", "waiterdb/avatica"]
DESCRIPTION = "waiter python client."
KEYWORDS = "waiter python package"
AUTHOR = "zhujiajunup"
AUTHOR_EMAIL = "zhujiajunup@163.com"
VERSION = '1.0.4'
LICENSE = "MIT"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description='waiter python client',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 3"
    ],
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=True,
)