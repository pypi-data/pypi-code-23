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

import os
import unittest

from ..directory import ChangeDirectory


class TestChangeDirectory( unittest.TestCase ) :
    def setUp( self ) :
        self.changeDirUnderTest = ChangeDirectory( '..' )


    def testDirectoryChanged( self ) :
        currentDirectory = os.path.realpath( os.path.abspath( os.path.curdir ) )
        expectedDirectory = os.path.realpath( os.path.join( currentDirectory, '..' ) )

        with ChangeDirectory( '..' ) :
            actualDirectory = os.path.realpath( os.path.abspath( os.path.curdir ) )

        self.assertEqual( expectedDirectory, actualDirectory )


    def testDirectoryRestored( self ) :
        expectedDirectory = os.path.realpath( os.path.abspath( os.path.curdir ) )
        expectedChangedDirectory = os.path.realpath( os.path.join( expectedDirectory, '..' ) )

        with ChangeDirectory( '..' ) :
            changedDirectory = os.path.realpath( os.path.abspath( os.path.curdir ) )

        self.assertEqual( expectedChangedDirectory, changedDirectory )

        actualDirectory = os.path.realpath( os.path.abspath( os.path.curdir ) )
        self.assertEqual( expectedDirectory, actualDirectory )


if __name__ == '__main__' :
    unittest.main()
