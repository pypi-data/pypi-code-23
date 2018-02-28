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
"""
The Dynamics module contains a number of objects that are
designed to perform discretized real-time processing of
arbitrary functions.

DOC-TODO
"""

__all__ = [
	'Stop',
	'Function',
	'Integral', 'Impulse', 'Clock', 'Smoother', 'Oscillator',
	'Apply',
	'StateMachine',
]

from   copy import deepcopy
import math
import inspect
import weakref
import operator
import functools
import collections

numpy = None
try: import numpy
except: pass

IDCODE = property( lambda self: '0x%08x' % id( self ) )

class Stop( StopIteration ):
	"""
	This a type of Exception (specifically, a subclass of `StopIteration`).
	It is raised when a `Function`'s "watcher" callback (set using
	`Function.Watch()`) returns something other than `None`. Whatever the
	callback returns is used as constructor arguments.
	"""
	def __init__( self, *pargs, **kwargs ):
		StopIteration.__init__( self, *( pargs + ( kwargs, ) ) )
	
class Function( object ):
	"""
	DOC-TODO
	"""
	__slots__ = [ 'terms' ]
	_vanilla = True
	id = IDCODE
	
	def __init__( self, *pargs, **kwargs ):
		if not hasattr( self, 'terms' ): self._init( *pargs, **kwargs )	
	def _init( self, *pargs, **kwargs ):
		self.terms = []
		while pargs and self._vanilla:
			other = pargs[ 0 ]
			if not isinstance( other, type( self ) ) or not other._vanilla: break
			pargs = pargs[ 1: ]
			self.terms[ : ] = deepcopy( other.terms )
			if self.terms: break
		for arg in pargs:
			if kwargs and callable( arg ): arg = functools.partial( arg, **kwargs )
			self += arg
		return self

	def __call__( self, *pargs, **kwargs ):
		#print('%r is being called with %r and %r' % ( self, pargs, kwargs ))
		result = None
		for mode, opfunc, term in self.terms:
			if mode == 'through':
				pp, kk = opfunc
				opfunc = None
				term = term( result, *pp, **kk )
			elif mode == 'watch':
				pp, kk = opfunc
				opfunc = None
				if result is not None:
					stopValue = term( result, *pp, **kk )
					if isinstance( stopValue, ( tuple, list ) ) and any( isinstance( x, dict ) for x in stopValue ): raise Stop( *stopValue )
					elif stopValue is not None: raise Stop( stopValue )
				continue
			elif callable( term ):
				term = term( *pargs, **kwargs )
			if isinstance( term, Exception ): raise term
			if numpy is not None and term is not None and not isinstance( term, ( int, float, numpy.ndarray ) ):
				term = numpy.array( term, dtype=float, copy=False )
			if result is None or opfunc is None: result = term
			elif mode == 'LR':  result = opfunc( result, term )
			elif mode == 'RL':  result = opfunc( term, result )
			else: raise ValueError( 'internal error - unexpected mode' )
		return result
	
	def __repr__( self ): return '<%s %s>' % ( self.__class__.__name__, self.id )
	def __str__( self ):
		s = repr( self )
		for iTerm, ( mode, opfunc, term ) in enumerate( self.terms ):
			isLast = ( iTerm == len( self.terms ) - 1 )
			if mode == 'through':
				pp, kk = opfunc
				s += TreeBranch( 'through %s( <>%s%s )' % ( term.__name__, ''.join( ', %r' % arg for arg in pp ), ''.join( ', %s=%r' % item for item in kk.items() ) ) )
			else:
				if iTerm: s += TreeBranch( '%s %r' % ( mode, opfunc ) )
				s += TreeBranch( term, last=isLast )
		return s
		
	def __neg__( self ): return 0 - self
	def __pos__( self ): return self

	def Through( self, any_callable, *additional_pargs, **kwargs ):
		self.terms.append( ( 'through', ( additional_pargs, kwargs ), any_callable ) )
		return self
		
	def Watch( self, conditional, *additional_pargs, **kwargs ):
		"""
		DOC-TODO
		"""
		#TODO: need a demo of this in conjunction with PropertyManagement/Shady dynamics:
		#      functionInstance.Watch(
		#          lambda f:  None if f < 10 else [ f, {'visible':0} ]
		#      )
		self.terms.append( ( 'watch', ( additional_pargs, kwargs ), conditional ) )
		return self
		
		
def TreeBranch( txt, spacers=1, last=False ):
	blank   = '       '
	bar     = ' |     '
	branch  = ' +---- '
	indent  = blank if last else bar
	lines = str( txt ).replace( '\r\n', '\n' ).replace( '\r', '\n' ).split( '\n' )
	s = ( '\n' + bar ) * spacers + '\n'
	return s + '\n'.join( ( indent if iLine else branch ) + line for iLine, line in enumerate( lines ) )

def MakeOperatorMethod( optype, opname ):
	if opname == 'div': opname = 'truediv'
	opfunc = getattr( operator, opname )
	def func( instance, other ):
		if optype == 'i':
			mode = 'LR'
		else:
			if   optype == 'l': mode = 'LR'
			elif optype == 'r': mode = 'RL'
			else: raise ValueError( 'internal error - unexpected mode' )
			instance = deepcopy( instance )
		instance.terms.append( ( mode, opfunc, deepcopy( other ) ) )
		return instance
	return func
	
for opname in 'add sub mul truediv div floordiv pow mod'.split():
	setattr( Function, '__'  + opname + '__', MakeOperatorMethod( 'l', opname ) )
	setattr( Function, '__r' + opname + '__', MakeOperatorMethod( 'r', opname ) )
	setattr( Function, '__i' + opname + '__', MakeOperatorMethod( 'i', opname ) )

def Apply( any_callable, f, *additional_pargs, **kwargs ):
	"""
	DOC-TODO
	"""
	return deepcopy( f ).Through( any_callable, *additional_pargs, **kwargs )

class Impulse( Function ):
	"""
	A very simple `Function` subclass. Returns its constructor
	argument `magnitude` the first time it is called (or when
	called again with the same `t` argument as its first call).
	Returns `0.0` if called with any other value of `t`.
	"""
	def __init__( self, magnitude=1.0 ):
		self.__t0 = None
		self.__magnitude = magnitude
		super( Impulse, self ).__init__( self.__impulse )
	def __impulse( self, t, *pargs, **kwargs):
		if self.__t0 is None:  self.__t0 = t
		return self.__magnitude if t == self.__t0 else 0.0

def Sinusoid( cycles, phase_deg=0 ):
	"""
	Who enjoys typing `2.0 * numpy.pi *` over and over again?
	This is a wrapper around `numpy.sin` (or `math.sin` if `numpy`
	is not installed) which returns a sine function of an argument
	expressed in cycles (0 to 1 around the circle).  Heterogeneously,
	but hopefully intuitively, the optional phase-offset argument
	is expressed in degrees. If `numpy` is installed, either
	argument may be non-scalar (`phase_deg=[90,0]` is useful
	converting an angle into 2-D Cartesian coordinates).
	"""
	if numpy: return numpy.sin( 2.0 * numpy.pi * ( numpy.asarray( cycles, float ) + numpy.asarray( phase_deg, float ) / 360.0 ) )
	else:     return math.sin(  2.0 * math.pi  * ( float( cycles )                + float( phase_deg )                / 360.0 ) )
		
def Oscillator( freq, phase_deg=0.0 ):
	"""
	Returns a `Function` object with an oscillating output: the
	result of `Apply`ing `Sinusoid` to an `Integral`.
	"""
	return Apply( Sinusoid, Integral( freq ), phase_deg=phase_deg )

def Clock( startNow=True, speed=1.0 ):
	"""
	DOC-TODO
	"""
	if numpy: speed = numpy.asarray( speed, dtype=float )
	if startNow: return Integral( speed )
	else: return Function( lambda t: speed * t )

class Smoother( Function ):
	"""
	DOC-TODO
	"""
	def __new__( cls, arg=None, sigma=1.0, exponent=2.0 ):
		self = super( Smoother, cls ).__new__( cls )
		self.__init__( cls.SmoothingWrapper( arg, sigma=sigma, exponent=exponent ) )
		return self
	class SmoothingWrapper( object ):
		__slots__ = [ 'func', 'sigma', 'exponent', 'memory' ]
		id = IDCODE
		def __init__( self, func, sigma, exponent ):
			self.memory = {}
			self.func = func
			self.sigma = float( sigma )
			self.exponent = exponent
		def __repr__( self ): return '<%s %s>' % ( self.__class__.__name__, self.id )
		def __str__( self ): return repr( self ) + TreeBranch( self.func, last=True )
		def __call__( self, t, *pargs, **kwargs ):
			x, y = self.memory.get( t, ( None, None ) )
			if y is not None: return y
			if x is None:
				x = self.func
				if callable( x ): x = x( t, *pargs, **kwargs )
			if numpy: x = numpy.array( x, dtype=float, copy=True )
			if x is None or not self.sigma: return x
			self.memory[ t ] = ( x, None )
			if self.exponent is None: y = self.EWA( t )
			else: y = self.FIR( t )
			self.memory[ t ] = ( x, y )
			return y
		def FIR( self, t ): # Gaussian-weighted with sigma interpreted as standard deviation
			sumwx = sumw  = 0.0
			for ti, ( xi, yi ) in list( self.memory.items() ):
				nsig = abs( t - ti ) / self.sigma
				if nsig > 5.0: del self.memory[ ti ]; continue
				if self.sigma == 0.0: wi = 1.0
				else: wi = math.exp( -0.5 * nsig ** self.exponent )
				sumw  = sumw  + wi
				sumwx = sumwx + wi * xi
			return sumwx / sumw			
		def EWA( self, t ): # exponential weighted average (IIR of order 1) with sigma interpreted as half-life
			items = sorted( self.memory.items() )
			tcurr, ( xcurr, ycurr ) = items[ -1 ]
			if len( items ) == 1: return xcurr
			tprev, ( xprev, yprev ) = items[ -2 ]
			self.memory = dict( items[ -2: ] )
			lambda_ = 0.5 ** ( ( tcurr - tprev ) / self.sigma )
			return lambda_ * yprev + ( 1.0 - lambda_ ) * xcurr
			
			
			
class Integral( Function ):
	r"""
	A subclass of `Function`. Like its superclass, the terms it wraps
	may be numeric constants and/or callables that take a single numeric
	argument `t`.   The `Integral` instance is itself a callable object
	that can be called with `t`.  Unlike `Function`, however, an `Integral`
	has memory for values of `t` on which it has previously been called,
	and returns the *cumulative* area under the sum of its wrapped terms,
	estimated discretely via the trapezium rule at the distinct values
	of `t` for which the object is called.
	
	Like any `Function`, it can interact with other `Functions`, with other
	single-argument callables, with numeric constants, and with numeric
	`numpy` objects via the standard arithmetic operators `+`, `-`, `/`,
	`*`, `**`, and `%`, and may also have other functions applied to its
	output via `Apply`.
	
	An `Integral` may naturally be constructed around another `Integral`,
	or other type of `Function`.
	
	Example - prints samples from the quadratic :math:`\frac{1}{2}t^2 + 100`:: 
	    
	    g = Integral( lambda t: t ) + 100.0
	    print( g(0) )
	    print( g(0.5) )
	    print( g(1.0) )
	    print( g(1.5) )
	    print( g(2.0) )
	
	"""
	def __new__( cls, *pargs, **kwargs ):
		self = super( Integral, cls ).__new__( cls )
		if not pargs: pargs = ( 1, )
		self.__init__( *[ cls.IntegratingWrapper( arg ) for arg in pargs ], **kwargs )
		return self
	class IntegratingWrapper( object ):
		__slots__ = [ 'func', 't_prev', 'f_prev', 'y' ]
		id = IDCODE
		def __init__( self, func ):
			#print( '_Accumulator.__init__(%r, %r)' % ( self, func ) )
			self.func = func
			self.t_prev = None
			self.f_prev = None
			self.y = 0.0
		def __repr__( self ): return '<%s %s>' % ( self.__class__.__name__, self.id )
		def __str__( self ): return repr( self ) + TreeBranch( self.func, last=True )
		def __call__( self, t, *pargs, **kwargs ):
			#print('%r is being called with %r, %r and %r' % ( self, t, pargs, kwargs ))
			if self.t_prev is None: dt = None
			else: dt = t - self.t_prev
			self.t_prev = t
			value = self.func
			if callable( value ):
				#print( '%r is calling %r with %r, %r and %r' % ( self, value, t, pargs, kwargs ) )
				value = value( t, *pargs, **kwargs )
			if isinstance( value, Exception ): raise value
			if numpy is not None and value is not None and not isinstance( value, ( int, float, numpy.ndarray ) ):
				value = numpy.array( value, dtype=float, copy=False )
			# add trapezia (i.e. assume the function value climbed linearly to its current value over the interval since last call)
			if dt: self.y += ( self.f_prev + value ) * 0.5 * dt
			if dt or self.f_prev is None: self.f_prev = value				
			# comment out the two lines above, and uncomment the one below,sss to add rectangles (i.e. assume step changes to the given function value, held constant throughout each inter-call interval)
			#if dt: self.y += value * dt
			return self.y


class StateMachine( object ):
	"""
	DOC-TODO
	"""
	
	class Constant( object ):
		def __init__( self, name ): self.__name = name
		def __repr__( self ): return self.__name
	
	NEXT = Constant( 'StateMachine.NEXT' )
	PENDING = Constant( 'StateMachine.PENDING' )
	CANCEL = Constant( 'StateMachine.CANCEL' )
		
	class State( object ):
		
		next = None
		duration = None
		onset = None
		offset = None
		__machine = None
		__name = None
			
		def __init__( self, name=None, duration=None, next=None, onset=None, ongoing=None, offset=None, machine=None ):
			if name     is not None: self.__name = name
			if machine  is not None: self.__machine = weakref.ref( machine )
			self.__set( duration=duration, next=next, onset=onset, ongoing=ongoing, offset=offset )
		
		def __set( self, **kwargs ):
			for attrName, value in kwargs.items():
				if value is None: continue
				if callable( value ):
					try: inspect.getfullargspec
					except: args = inspect.getargspec( value ).args
					else:   args = inspect.getfullargspec( value ).args
					if len( args ): # this lets you set callables with either zero arguments or one argument (self) 
						if not hasattr( value, '__self__' ): value = value.__get__( self )
						if value.__self__ is not self: value = value.__func__.__get__( self )
				setattr( self, attrName, value )
		name                 = property( lambda self: self.__name if self.__name else self.__class__.__name__ )
		machine              = property( lambda self: self.__machine() )
		elapsed              = property( lambda self: self.__machine().elapsed_current )
		t                    = property( lambda self: self.__machine().t )
		fresh                = property( lambda self: self.__machine().fresh )
		Change = ChangeState = property( lambda self: self.__machine().ChangeState )
				
		def __eq__( self, other ):
			if isinstance( other, str ): return self.name.lower() == other.lower()
			else: return self is other
				
	def __init__( self, *states ):
		self.__states = {}
		self.__current = None
		self.__first_call_time = None
		self.__call_time = None
		self.__change_time = None
		self.__change_call_time = None
		self.__change_pending = []
		for arg in states:
			for state in ( arg if isinstance( arg, ( tuple, list ) ) else [ arg ] ):
				self.AddState( state )
			
	def AddState( self, name, duration=None, next=None, onset=None, ongoing=None, offset=None ):
		if isinstance( name, ( type, StateMachine.State ) ):
			state = name() if isinstance( name, type ) else name 
			if not isinstance( state, StateMachine.State ): raise TypeError( 'if you use classes to define your states, they must be subclasses of StateMachine.State' )
			StateMachine.State.__init__( state, name=None, duration=duration, next=next, onset=onset, ongoing=ongoing, offset=offset, machine=self )
		else: state = StateMachine.State( name=name,       duration=duration, next=next, onset=onset, ongoing=ongoing, offset=offset, machine=self )
		if not self.__states: self.ChangeState( state.name )
		self.__states[ state.name ] = state
		return state
	
	def ChangeState( self, newState=NEXT, timeOfChange=PENDING ):
		if newState is StateMachine.NEXT:
			newState = getattr( self.__current, 'next', None )
		if timeOfChange is StateMachine.PENDING:
			self.__change_pending.append( newState )
			return StateMachine.PENDING
		if callable( newState ):
			newState = newState()
		if isinstance( newState, StateMachine.State ):
			newState = newState.name
		if newState is StateMachine.CANCEL:
			return StateMachine.CANCEL
		if newState is not None:
			newState = self.__states[ newState ]
		if not( self.__current is None and newState is None ):
			if timeOfChange is None: timeOfChange = self.__call_time
			self.__change_time = timeOfChange
			self.__change_call_time = self.__call_time
		offset = getattr( self.__current, 'offset', None )
		if callable( offset ): offset()
		self.__current = newState
		onset = getattr( self.__current, 'onset', None )
		if callable( onset ): onset()
		return newState
	
	t = property( lambda self: self.__call_time )
	state = current = property( lambda self: self.__current )	
	fresh = property( lambda self: self.__change_call_time == self.__call_time )
	elapsed_current = property( lambda self: None if ( self.__call_time is None or self.__change_time     is None ) else self.__call_time - self.__change_time )
	elapsed_total   = property( lambda self: None if ( self.__call_time is None or self.__first_call_time is None ) else self.__call_time - self.__first_call_time )
		
	def __call__( self, t ):
		if self.__call_time == t: return self.__current
			
		self.__call_time = t
		if self.__first_call_time is None:
			self.__first_call_time = self.__change_time = self.__change_call_time = t
		while self.__change_pending:
			self.ChangeState( newState=self.__change_pending.pop( 0 ), timeOfChange=t )
		
		# Note there's more than one way to change state - in descending order of recommendedness:
		# - you can rely on state.duration and state.next,
		# - or (for more dynamic behaviour) you can return a state name from state.ongoing(),
		# - or you can make an explicit call to machine.ChangeState(...) during your main loop,
		# - or you can make an explicit call to self.Change(...) during state.ongoing(), or even
		#   during state.onset() or state.offset() if you somehow absolutely must.
		# Note to maintainers: in principle you could *approximate* the function of .duration
		# and .next just by setting
		#   ongoing = lambda self: 'SomeNewState' if self.elapsed >= someDuration else None
		# but do not imagine that .duration and .next are redundant: having them as explicit
		# attributes and using the timeOfOrigin shuffle below allows transitions to be
		# performed in such a way that quantization errors in state durations do not
		# accumulate over time:
		
		while True:
			
			duration = getattr( self.__current, 'duration', None )
			if callable( duration ): duration = duration()
			if duration is not None and self.elapsed_current is not None and self.elapsed_current >= duration:
				timeOfOrigin = self.__change_time
				if timeOfOrigin is None: timeOfOrigin = self.__first_call_time
				timeOfChange = timeOfOrigin + duration
				self.ChangeState( newState=self.__current.next, timeOfChange=timeOfChange )
	
			ongoing = getattr( self.__current, 'ongoing', None )
			if not callable( ongoing ): break
			newState = ongoing()
			if not newState: break
			if self.ChangeState( newState=newState, timeOfChange=t ) is StateMachine.CANCEL: break
			
		return self.__current

def StateMachineDemo():
	"""
	DOC-TODO
	"""
	sm = StateMachine()
	sm.AddState( 'first',  duration=123, next='second' )
	sm.AddState( 'second', duration=234, next='third' )
	sm.AddState( 'third',  duration=345, next='first' )
	import numpy; print( numpy.cumsum( [ 123, 234, 345, 123, 234, 345 ] ) )
	for t in range( 0, 1000, 2 ):
		state = sm( t )
		state = sm( t ) # it doesn't matter how many times the machine is queried with
		                # the same t: the change happens only once, and "fresh"-ness
		                # of the state persists until called with a different t
		if state.fresh:
			if state == 'first': print( 'passing GO, collecting $200' )
			print( '%5g: %s (elapsed = %r)' % ( t, state.name, state.elapsed ) )

if __name__ == '__main__':
	p = Apply( numpy.sin, Integral( Integral( 0.05 ) ) + [ numpy.pi / 2, 0] ) * 500
	
	print( p )
	print( p(0) )
	print( p(1) )
	print( p(2) )

