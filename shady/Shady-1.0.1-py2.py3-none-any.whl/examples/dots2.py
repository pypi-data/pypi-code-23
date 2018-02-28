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

class DotWorld( Shady.World ):
	def RandomPosition( self ):
		return self.Place( numpy.random.rand( 2 ) * 2.0 - 1.0 )
	def RandomVelocity( self, thetaMean, thetaStd, speedMean, speedStd ):
		speed = numpy.random.randn() * speedStd + speedMean
		theta = numpy.random.randn() * thetaStd + thetaMean
		theta *= numpy.pi / 180.0
		return speed * numpy.array( [ numpy.cos( theta ), numpy.sin( theta ) ] )
	def Prepare( self, ndots=500, loop=False ):
		self.anchor = -1
		self.Set( gamma=2.2, bg=0.5 )
		self.dots = [ self.Stimulus(
			name = 'dot%04d',
			size = 50,
			scaledSize = 50,
			color = numpy.random.rand(3),
			bgalpha = 0,
			pp = float( i ) / ndots,
			debugTiming = False,
			gamma = self,
			bg = self,
			noise = self,
		) for i in range( ndots ) ]
		self.start    = numpy.array( [ self.RandomPosition() for dot in self.dots ] )
		self.velocity = numpy.array( [ self.RandomVelocity( 270.0, 10.0, 125.0, 10.0 ) for dot in self.dots ] )
		self.batch = self.CreatePropertyArray( 'envelopeTranslation', self.dots ) # could use 'envelopeTranslation' or 'envelopeOrigin'
		self.allPositions = self.batch.A[ : , :2 ]
		self.allPositions[ : ] = self.start 
		self.each = list( zip( self.allPositions, self.start, self.velocity ) )
		self.SetSwapInterval( 2 ) # needs accelerator (NB: seems to fail on mac)
		self.captured = []
		def AnimateEach( self, t ):
			for position, start, velocity in self.each: position[ : ] = ( start + velocity * t ) % self.size
		def AnimateAll( self, t ):
			self.allPositions[ : ] = ( self.start + self.velocity * t ) % [ self.size ]
		if loop: self.SetAnimateMethod( AnimateEach )
		else:    self.SetAnimateMethod( AnimateAll )
			
	def HandleEvent( self, event ):
		if event.type == 'key_release':
			if event.key in [ 'q', 'escape' ]: self.Close()
			elif event.key in [ 'f' ]: self.Faces()
	
if __name__ == '__main__':
	cmdline = Shady.WorldConstructorCommandLine( canvas=True, debugTiming=True )
	cmdline.Option( 'ndots', 300,   type=int )
	cmdline.Option( 'loop',  False, type=bool )
	shell = cmdline.Option( 'shell', False, type=bool, container=None )
	textured = cmdline.Option( 'textured', False, type=bool, container=None )
	cmdline.Finalize()
	
	w = DotWorld( **cmdline.opts )
	if textured:
		master = w.dots[ -1 ]
		master.LoadTexture( Shady.PackagePath( 'examples/media/face.png' ), False )
		master.ShareProperties( w.dots, 'textureSlotNumber', 'textureID', 'useTexture' ) 
		master.cr = Shady.Clock( speed=90 )
		
	Shady.AutoFinish( w, shell=shell )
