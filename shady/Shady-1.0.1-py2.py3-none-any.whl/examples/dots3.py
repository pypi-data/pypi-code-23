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
import numpy
import Shady

def RandomPosition( max=1.0, n=1 ):
	return numpy.random.rand( n, 2 ) * max
	
def RandomVelocity( thetaMean=270, thetaStd=10, speedMean=125, speedStd=10, n=1 ):
	speed = numpy.random.randn( n, 1 ) * speedStd + speedMean
	theta = numpy.random.randn( n, 1 ) * thetaStd + thetaMean
	theta *= numpy.pi / 180.0
	return speed * numpy.hstack( [ numpy.cos( theta ), numpy.sin( theta ) ] )

def AsComplex( x ):
	""" Convert an n-by-2 array of real-valued coordinates to a 1-D array of complex numbers."""
	return numpy.dot( x, [ 1.0, 1.0j ] )
def AsReal( x ):
	""" Convert a 1-D array of complex numbers an n-by-2 array of real-valued coordinates."""
	return numpy.c_[ x.real.flat, x.imag.flat ]


if __name__ == '__main__':
	cmdline = Shady.WorldConstructorCommandLine( canvas=True, debugTiming=True )
	ndots  = cmdline.Option( 'ndots', 300,   type=int, container=None )
	nsides = cmdline.Option( 'sides',   5,   type=int, min=3, container=None )
	radius = cmdline.Option( 'radius', 25.0, type=( int, float ), container=None )
	spin   = cmdline.Option( 'spin',    0.2, type=( int, float ), container=None )
	shell  = cmdline.Option( 'shell', False, type=bool, container=None )
	cmdline.Finalize()

	w = Shady.World( **cmdline.opts )
	
	#field = w.Stimulus( size=w.size, color=1 )
	field = w.Stimulus( Shady.PackagePath( 'examples/media/waves.jpg' ), visible=0 )
	field.Set( anchor=-1, position=field.Place( -1 ) )  # still centered on the screen, but now
	                                                    # the "anchor" position is bottom left
	                                                    # (makes coordinate juggling easier below)
	field.cscale = max( w.size.astype( float ) / field.textureSize )
	circ = numpy.linspace( 0.0, 1.0, nsides + 1, endpoint=True )
	circ.flat[ -1 ] = numpy.nan  # NaNs define the breaks between polygons
	shape = radius * numpy.exp( circ * numpy.pi * 2.0j )
	locations = RandomPosition( max=field.size, n=ndots )
	velocity = RandomVelocity( n=ndots )
	
	f = Shady.Integral( lambda t: velocity ) + locations
	f %= [ field.size ]
	f = Shady.Apply( lambda centers: AsComplex( centers )[ :, None ],  f )
	f += lambda t: shape[ None, : ] * 1j ** ( 2.0 * numpy.pi * spin * t )
	field.Set( points=f, drawMode=Shady.DRAWMODE.POLYGON, visible=1 )

	Shady.AutoFinish( w, shell=shell )
