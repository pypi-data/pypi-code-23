#
# Copyright 2017 Russell Smiley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import unittest

from ..exclude import applyRecursiveExclusions


class TestApplyRecursiveExclusions( unittest.TestCase ) :
    def testGlobalExclude( self ) :
        directory = '.'
        inputNames = {
            os.path.join( 'one' ),
            os.path.join( 'subdir', 'two' ),
            os.path.join( 'sub', 'subdir', 'three' ),
            os.path.join( 'subdir', 'four' ),
            os.path.join( 'twice' ),
        }
        exclusions = [ 't*' ]
        expectedValue = {
            os.path.join( 'one' ),
            os.path.join( 'subdir', 'four' ),
        }

        actualValue = set( applyRecursiveExclusions( inputNames, directory, exclusions ) )

        self.assertEqual( { os.path.normpath( x ) for x in expectedValue }, actualValue )


    def testSubdirExclude( self ) :
        directory = 'subdir'
        inputNames = {
            os.path.join( 'one' ),
            os.path.join( 'subdir', 'two' ),
            os.path.join( 'subdir', 'sub', 'three' ),
            os.path.join( 'subdir', 'four' ),
            os.path.join( 'twice' ),
        }
        exclusions = [ 't*' ]
        expectedValue = {
            os.path.join( 'one' ),
            os.path.join( 'subdir', 'four' ),
            os.path.join( 'twice' ),
        }

        actualValue = set( applyRecursiveExclusions( inputNames, directory, exclusions ) )

        self.assertEqual( { os.path.normpath( x ) for x in expectedValue }, actualValue )


    def testDirExcludeNotMatched( self ) :
        directory = '.'
        inputNames = {
            os.path.join( 'file' ),
            os.path.join( 'subdir', 'two' ),
            os.path.join( 'subdir', 'file', 'three' ),
            os.path.join( 'subdir', 'file' ),
            os.path.join( 'twice' ),
        }
        exclusions = [ 'file' ]
        expectedValue = {
            os.path.join( 'twice' ),
            os.path.join( 'subdir', 'two' ),
            os.path.join( 'subdir', 'file', 'three' ),
        }

        actualValue = set( applyRecursiveExclusions( inputNames, directory, exclusions ) )

        self.assertEqual( { os.path.normpath( x ) for x in expectedValue }, actualValue )


if __name__ == '__main__' :
    unittest.main()
