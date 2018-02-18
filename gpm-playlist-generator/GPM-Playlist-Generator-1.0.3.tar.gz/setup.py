#!/usr/bin/env python

from setuptools import find_packages, setup
import distutils.cmd
from distutils import log
from distutils.version import StrictVersion
from pip.commands.search import SearchCommand, transform_hits, highest_version

PACKAGE_NAME = 'GPM-Playlist-Generator'

about = {}
with open('gpmplgen/__version__.py') as f:
    exec(f.read(), about)

VERSION = about['__version__']

def readme():
    with open('README.rst') as f:
        return f.read()


class CheckLatestVersionCommand(distutils.cmd.Command):

    description = 'check that the version specified is higher than the one on PiPy'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pkg_name = self.distribution.get_name()
        pkg_version = self.distribution.get_version()
        search = SearchCommand()
        options, _ = search.parse_args([pkg_name])
        pypi_hits = search.search(pkg_name, options)
        hits = transform_hits(pypi_hits)

        remote_version = None
        for hit in hits:
            if hit['name'] == pkg_name:
                remote_version = highest_version(hit['versions'])
                self.announce("Found %s version %s on PyPi" % (pkg_name, remote_version), log.INFO)
        if remote_version is None:
            raise RuntimeError("Could not found %s on PyPi" % pkg_name)
        if StrictVersion(VERSION) <= StrictVersion(remote_version):
            raise VersionError("Local version %s not greater than PyPi version %s" % (pkg_version, remote_version))
        self.announce("Local version %s higher than PyPi version" % pkg_version)


class VersionError(RuntimeError):
    pass

setup(name=PACKAGE_NAME,
      version=VERSION,
      description='Google Play Music - Playlist Generator',
      long_description = readme(),
      author='Hugo Haas',
      author_email='hugoh@hugoh.net',
      url='https://gitlab.com/hugoh/gpm-playlistgen',
      packages=find_packages(exclude=('tests',)),
      scripts=[
          'scripts/gpm-playlistgen.py'
      ],
      install_requires=[
          'gmusicapi',
          'pyyaml'
      ],
      keywords=['google music', 'google play music', 'playlist', 'playlist generator'],
      classifiers=[
          'Environment :: Console',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Intended Audience :: End Users/Desktop',
          'Topic :: Multimedia :: Sound/Audio',
      ],
      cmdclass={
          'check_latest_version': CheckLatestVersionCommand,
      }
      )
