#
# Copyright 2018 Russell Smiley
#
# This file is part of distributionPackage.
#
# distributionPackage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# distributionPackage is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with distributionPackage.  If not, see <http://www.gnu.org/licenses/>.
#

import argparse

from .options import PackageOptions


def parseArguments( arguments ) :
    parser = argparse.ArgumentParser( description = 'Build a distribution package from a manifest' )
    parser.add_argument( '-m', '--manifest',
                         default = 'manifest.yml',
                         dest = 'manifest',
                         help = 'Manifest file to use to build the package (default manifest.yml)' )
    parser.add_argument( '-o', '--output',
                         default = '.',
                         help = 'Directory to place the generated distribution files. Created if not present. (default ./)' )
    parser.add_argument( '-p', '--package',
                         default = 'distribution-out',
                         help = 'Filename stub of output package, not including suffix or version info (default distribution-out)' )
    parser.add_argument( '-r', '--project-root',
                         default = '.',
                         dest = 'projectRoot',
                         help = 'Project root to package files from (default ./)' )
    parser.add_argument( '-n', '--no-tar',
                         action = 'store_false',
                         default = True,
                         dest = 'tar',
                         help = 'Disable tar, gzip output distribution (default enabled)' )
    parser.add_argument( '-z', '--zip',
                         action = 'store_true',
                         default = False,
                         help = 'Enable zip output distribution (default disabled)' )

    args = parser.parse_args( arguments )

    packageOptions = PackageOptions()
    packageOptions.manifest = args.manifest
    packageOptions.output = args.output
    packageOptions.package = args.package
    packageOptions.projectRoot = args.projectRoot
    packageOptions.isTarFile = args.tar
    packageOptions.isZipFile = args.zip

    return packageOptions
