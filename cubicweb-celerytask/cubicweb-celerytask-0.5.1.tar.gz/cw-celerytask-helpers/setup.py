from setuptools import setup, find_packages

from cw_celerytask_helpers import __pkginfo__ as pkginfo

setup(
    name=pkginfo.distname,
    version=pkginfo.version,
    description=pkginfo.description,
    author=pkginfo.author,
    author_email=pkginfo.author,
    license=pkginfo.license,
    classifiers=pkginfo.classifiers,
    packages=find_packages('.'),
    install_requires=pkginfo.__depends__,
)
