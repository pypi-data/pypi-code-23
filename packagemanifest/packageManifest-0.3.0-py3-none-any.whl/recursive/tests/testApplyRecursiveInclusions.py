#
# Copyright 2017 Russell Smiley
#
# This file is part of package-manifest.
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

from ..include import applyRecursiveInclusions


class TestRecursiveInclude( unittest.TestCase ) :
    def testGlobalInclude( self ) :
        directory = '.'
        inputNames = {
            os.path.join( 'one' ),
            os.path.join( 'subdir', 'two' ),
            os.path.join( 'sub', 'subdir', 'three' ),
            os.path.join( 'subdir', 'four' ),
            os.path.join( 'twice' ),
        }
        inclusions = [ 't*' ]
        expectedValue = {
            os.path.join( 'subdir', 'two' ),
            os.path.join( 'twice' ),
            os.path.join( 'sub', 'subdir', 'three' ),
        }

        actualValue = set( applyRecursiveInclusions( inputNames, directory, inclusions ) )

        self.assertEqual( { os.path.normpath( x ) for x in expectedValue }, actualValue )


    def testSubdirInclude( self ) :
        directory = 'subdir'
        inputNames = {
            os.path.join( 'one' ),
            os.path.join( 'subdir', 'two' ),
            os.path.join( 'subdir', 'sub', 'three' ),
            os.path.join( 'subdir', 'four' ),
            os.path.join( 'twice' ),
        }
        inclusions = [ 't*' ]
        expectedValue = {
            os.path.join( 'subdir', 'two' ),
            os.path.join( 'subdir', 'sub', 'three' ),
        }

        actualValue = set( applyRecursiveInclusions( inputNames, directory, inclusions ) )

        self.assertEqual( { os.path.normpath( x ) for x in expectedValue }, actualValue )


    def testDirIncludeNotMatched( self ) :
        directory = '.'
        inputNames = {
            os.path.join( 'file' ),
            os.path.join( 'subdir', 'two' ),
            os.path.join( 'subdir', 'file', 'three' ),
            os.path.join( 'subdir', 'file' ),
            os.path.join( 'twice' ),
        }
        inclusions = [ 'file' ]
        expectedValue = {
            os.path.join( 'file' ),
            os.path.join( 'subdir', 'file' ),
        }

        actualValue = set( applyRecursiveInclusions( inputNames, directory, inclusions ) )

        self.assertEqual( { os.path.normpath( x ) for x in expectedValue }, actualValue )


if __name__ == '__main__' :
    unittest.main()
