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
import Shady
from Shady.Dynamics import Function, Integral, Apply, StateMachine


cmdline = Shady.WorldConstructorCommandLine()
shell = cmdline.Option( 'shell', False,  type=bool, container=None )
cmdline.Finalize()

w = Shady.World( **cmdline.opts )
s = w.Stimulus( Shady.PackagePath( 'examples/media/alien1/*' ), x=-w.width/2 )

def ExitSpiral( state ):
	if state.elapsed < 3: return StateMachine.CANCEL
	return 'stand'


sm = StateMachine()
sm.AddState( 'stand', next='run' )
sm.AddState( 'run',  duration=2, next='jump' )
sm.AddState( 'jump', duration=0.4, next='fall' )
sm.AddState( 'fall', duration=3, next='stand' )
sm.AddState( 'spiral', next=ExitSpiral )


def RunningJump( sprite, t ):
	state = sm( t )
	if state.fresh:
		if state == 'stand': sprite.xy = 0; sprite.Set( x = -w.width/2 + 100, y=0, frame=0 )
		if state == 'run':   sprite.Set( x=Integral( 400 ) + sprite.x, frame=Integral( 30 ) )
		if state == 'jump':  sprite.Set( y=Integral( Integral( -5000 ) + 1500 ) + sprite.y,  frame=0 )
		if state == 'fall':  sprite.frame = Integral( 160 )
		if state == 'spiral':
			radius = min( w.width, w.height ) / 2 - 100
			sprite.Set( x=-radius, y=0, frame=0 )
			sprite.xy = Apply( Shady.Sinusoid, Integral( Integral( 0.1 ) ), [ 270, 180 ] ) * Apply( max, radius - Integral( 20 ), 0 )
s.SetAnimateMethod( RunningJump )

def HandleEvent( self, event ):
	if event.type == 'text' and event.text==' ':
		if sm.state in [ 'stand', 'run', 'spiral' ]: sm.ChangeState()
	elif event.type == 'key_release' and event.key in [ 'enter', 'return' ]:
		sm.ChangeState( 'spiral' )
	elif event.type == 'key_release' and event.key in [ 'q', 'escape' ]:
		self.Close()
w.SetEventHandler( HandleEvent )

Shady.AutoFinish( w, shell=shell )
