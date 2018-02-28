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
import random
import Shady
from Shady.Dynamics import Integral, Apply, StateMachine


cmdline = Shady.WorldConstructorCommandLine()
shell = cmdline.Option( 'shell', False,  type=bool, container=None )
cmdline.Finalize()

w = Shady.World( **cmdline.opts )
s = w.Stimulus( Shady.PackagePath( 'examples/media/alien1.gif' ), x=-w.width / 2 )

class Stand( StateMachine.State ):
	next = 'Run'

	def onset( self ):
		s.xy = 0
		s.Set( x=-w.width / 2 + 100, y=0, frame=0 )


class Run( StateMachine.State ):
	duration = 3.5
	next = 'Jump'

	def onset( self ):
		gait = lambda t: 1 if s.frame in [ 0, 12 ] else 10
		s.Set( x=Integral( gait ) * 40 + s.x, frame=Integral( gait ) * 3 + 1 )


class Jump( StateMachine.State ):
	duration = 0.4
	next = 'Fall'

	def onset( self ):
		s.Set( y=Integral( Integral(-5000) + 1500 ) + s.y, frame=0 )


class Fall( StateMachine.State ):
	duration = 3
	next = 'Stand'

	def onset( self ):
		s.frame = Integral(160)

	def offset( self ):
		w.clearColor = [ random.random(), random.random(), random.random() ]

	def ongoing( self ):
		if s.y < -w.height / 2: return 'Stand'


class Spiral( StateMachine.State ):

	def next( self ):
		if self.elapsed < 3:
			return StateMachine.CANCEL
		return 'Stand'

	def onset( self ):
		radius = min( w.size ) / 2 - 100
		s.Set( x=-radius, y=0, frame=0 )
		s.xy = Apply( Shady.Sinusoid, Integral( Integral( 0.1 ) ), [ 270, 180 ] ) * Apply( max, radius - Integral( 20 ), 0 )

sm = StateMachine( Stand, Run, Jump, Fall, Spiral )
# you could alternatively define sm = StateMachine() at the top and then decorate each State subclass with @sm.AddState

s.Animate = sm


def HandleEvent( self, event ):
	if event.type == 'text' and event.text == ' ':
		if sm.state in [ 'Stand', 'Run', 'Spiral' ]:
			sm.ChangeState()
	elif event.type == 'key_release' and event.key in [ 'enter', 'return' ]:
		sm.ChangeState( 'Spiral' )
	elif event.type == 'key_release' and event.key in [ 'q', 'escape' ]:
		self.Close()
w.SetEventHandler(HandleEvent)

Shady.AutoFinish( w, shell=shell )
