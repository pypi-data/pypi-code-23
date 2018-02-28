# $BEGIN_SHADY_LICENSE$
# 
# This file is part of the Shady project, a Python framework for
# real-time manipulation of psychophysical stimuli for vision science.
# 
# Copyright (C) 2017-18  Jeremy Hill, Scott Mooney
# 
# Shady is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# $END_SHADY_LICENSE$
__all__ = [
	'numpy',
	'Image', 'ImageGrab', 'ImageDraw', 'ImageFont',
]

import sys

from . import DependencyManagement; from .DependencyManagement import Import, RegisterVersion

numpy = Import( 'numpy', registerVersion=True )

Image     = Import( 'Image',     'PIL.Image',     packageName=[ 'PIL', 'pillow' ] )
ImageGrab = Import( 'ImageGrab', 'PIL.ImageGrab', packageName=[ 'PIL', 'pillow' ] )
ImageDraw = Import( 'ImageDraw', 'PIL.ImageDraw', packageName=[ 'PIL', 'pillow' ] )
ImageFont = Import( 'ImageFont', 'PIL.ImageFont', packageName=[ 'PIL', 'pillow' ] )
if Image:
	RegisterVersion( name='pillow', value=getattr( Image, 'PILLOW_VERSION', None ) )
	RegisterVersion( sys.modules.get( 'PIL', None ) )
	RegisterVersion( Image, 'VERSION' )

if ImageFont:
	try:
		ImageFont.truetype( 'blah', 12 )
	except ImportError as err:
		ImageFont = DependencyManagement.ModuleNotAvailable( 'PIL.ImageFont', packageName=[ 'PIL', 'pillow' ], broken=str( err ) )
	except:
		pass  # sure, you can't find 'blah'