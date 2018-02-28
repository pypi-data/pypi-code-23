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

physics = dict( exponent=10, closest=10, coefficient=800 )
def Accel( t=None ):
	p = field.pointsComplex
	d = p[ None, : ] - p[ :, None ]
	m = numpy.abs( d )
	degenerate = m < 1e-4
	nondegenerate = ~degenerate
	d[ nondegenerate ] /= m[ nondegenerate ] # d is now unit vectors
	m[ degenerate ] = numpy.inf
	m = numpy.clip( m - field.penThickness / 2.0, physics[ 'closest' ], numpy.inf )
	m /= physics[ 'closest' ]
	m **= -physics[ 'exponent' ] # m is now inverse square distance, with 0s on diagonal
	force = m * d * physics[ 'coefficient' ]
	force = force.sum( axis=0 )
	return numpy.c_[ force.real, force.imag ]

def Bounce( **kwargs ):
	physics.update( kwargs )
	field.points = ( Shady.Integral( Shady.Integral( Accel ), lambda t: velocity ) + field.points ) % [ field.size ]

if __name__ == '__main__':
	cmdline = Shady.WorldConstructorCommandLine( canvas=True, debugTiming=True )
	ndots = cmdline.Option( 'ndots', 300, type=int, container=None )
	bounce = cmdline.Option( 'bounce', False, type=bool, container=None )
	shell = cmdline.Option( 'shell', False, type=bool, container=None )
	cmdline.Finalize()

	w = Shady.World( anchor=-1, **cmdline.opts )
	field = w.Stimulus( color=1, drawMode=Shady.DRAWMODE.POINTS, penThickness=20, smoothing=True )
	field.points = RandomPosition( max=w.size, n=ndots )
	velocity = RandomVelocity( n=ndots )
	field.points = ( Shady.Integral( velocity ) + field.points ) % [ w.size ]

	if bounce: Bounce()
	Shady.AutoFinish( w, shell=shell )
