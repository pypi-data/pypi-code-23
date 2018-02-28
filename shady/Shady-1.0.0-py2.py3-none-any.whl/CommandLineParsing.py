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
	'CommandLine',
]
import sys
import ast
import copy
import shlex


Unspecified = object()
Taken = object()
class CommandLineError( Exception ): pass
class CommandLineValueError( CommandLineError ):
	def __init__( self, arg, explanation ):
		CommandLineError.__init__( self, 'illegal value in command-line option %s (%s)' % ( arg, explanation ) )
		
def AlternativesString( sequence, transformation=repr ):
	sequence = [ transformation( x ) for x in sequence ]
	return ', '.join( sequence[ :-1 ] ) + ( len( sequence ) > 1 and ' or ' or '' ) + sequence[ -1 ]

class OptionSchema( object ):
	def __init__( self, default_position, dashes, **kwargs ):
		self.__dict__.update( { k : Unspecified for k in 'name default position type min max values length minlength maxlength allowpartial casesensitive'.split() } )
		spec = sorted( kwargs.items() )
		for k, v in spec:
			invk = k.lower().replace( '_', '' )
			if invk not in self.__dict__:
				if k.startswith( '_' ): raise ValueError( 'unrecognized attribute %r' % k )
				#elif self.name is Unspecified: self.name, self.default = k, v; continue
				else: raise ValueError( 'unrecognized attribute %r (cannot interpret it as the option name, because %r has already been used for this)' % ( k, self.name ) )
			previousValue = self.__dict__[ invk ]
			if previousValue is Unspecified: self.__dict__[ invk ] = v
			#elif self.name is Unspecified and not k.startswith( '_' ): self.name, self.default = k, v; continue
			else: raise ValueError( 'duplicate attribute %r: %s=%r has already been set' % ( k, invk, previousValue ) )
		if self.name is Unspecified: raise ValueError( 'no name was specified for this option' )
		if self.default is Unspecified and self.position is Unspecified:  self.position = default_position
		self.dashes = dashes
		if self.type is Unspecified: self.type = ()
		elif not isinstance( self.type, ( tuple, list ) ): self.type = [ self.type ]
		if self.values is Unspecified: self.values = ()
		elif not isinstance( self.values, ( tuple, list ) ): self.values = [ self.values ]
		if self.length is Unspecified: self.length = ()
		elif not isinstance( self.length, ( tuple, list ) ): self.length = [ self.length ]
		if self.allowpartial  is Unspecified: self.allowpartial  = True
		if self.casesensitive is Unspecified: self.casesensitive = False
	def Resolve( self, args_p, args_k, optsOut=None ):
		prefixes = tuple( [ '-' * n + self.name for n in self.dashes ] )
		sources = []
		value = Unspecified
		for arg in args_k[ ::-1 ]:
			if arg.startswith( prefixes ):
				sources.append( arg )
				if value is Unspecified:
					matchedArg = arg
					value = arg.lstrip( '-' )[ len( self.name ): ]
					if len( value ) == 0: value = True  # so --verbose ends up the same as --verbose=1
					elif value.startswith( '=' ): value = value[ 1: ]
		if value is Unspecified:
			if self.position is not Unspecified and 0 <= self.position < len( args_p ):
				sources.append( self.position )
				value = args_p[ self.position ]
				matchedArg = repr( value )
			elif self.default is not Unspecified:
				value = self.default
				matchedArg = 'default value'
			else: raise CommandLineError( 'option %r was not specified on the command line, and has no default value' % self.name )
		if isinstance( value, str ):
			try: literal = ast.literal_eval( value )
			except: literal = Unspecified
		else: literal = value
		if self.type:
			for t in self.type:
				if t in [ None ] and literal is None: value = None; break
				if t in [ bool ] and literal in [ True, False ]: value = bool( literal ); break 
				if t in [ str ]:
					if isinstance( literal, str ): value = literal
					if self.values:
						transform = str if self.casesensitive else ( lambda x: str( x ).lower() )
						def match( allowed, incoming ):
							allowed, incoming = transform( allowed ), transform( incoming )
							if incoming == allowed: return True
							return self.allowpartial and incoming and allowed.startswith( incoming )
						matched = [ s for s in self.values if match( s, value ) ]
						if len( matched ) == 1: value = matched[ 0 ]
						elif len( matched ) > 1: raise CommandLineValueError( matchedArg, 'ambiguous - could match ' + AlternativesString( matched ) )
						else: raise CommandLineValueError( matchedArg, 'must be ' + AlternativesString( self.values ) )
					break
				if t in [ int, float, bool ]:
					try: numeric = float( value )
					except: continue
					if t is not float and numeric != t( numeric ): continue
					value = t( numeric )
					if self.min is not Unspecified and value < self.min: raise CommandLineValueError( matchedArg, 'minimum is %r' % self.min )
					if self.max is not Unspecified and value > self.max: raise CommandLineValueError( matchedArg, 'maximum is %r' % self.max )
					break
				if isinstance( t, type ) and isinstance( literal, t ) and literal is not Unspecified: value = literal; break
			else:
				raise CommandLineValueError( matchedArg, 'could not interpret as ' + AlternativesString( self.type, lambda t: getattr( t, '__name__', t.__class__.__name__ ) ) )
		if not isinstance( value, str ) and self.values and value not in self.values: raise CommandLineValueError( matchedArg, 'must be ' + AlternativesString( self.values ) )
		try: length = len( value )
		except: pass
		else:
			if self.length and length not in self.length: raise CommandLineValueError( matchedArg, 'length must be ' + AlternativesString( self.length ) )
			if self.minlength is not Unspecified and length < self.minlength: raise CommandLineValueError( matchedArg, 'length cannot be less than %r'    % self.minlength )
			if self.maxlength is not Unspecified and length > self.maxlength: raise CommandLineValueError( matchedArg, 'length cannot be greater than %r' % self.maxlength )
		if optsOut is not None: optsOut[ self.name ] = value
		return sources, value

	
class Bunch( dict ):
	def __init__( self, *pargs, **kwargs ): self.__dict__ = self.update( *pargs, **kwargs )
	def update( self, *pargs, **kwargs ): [ dict.update( self, d ) for d in pargs + ( kwargs, ) ]; return self
	def release( self ): self.__dict__ = {} # call this to remove the circular self-reference and allow the object to be deleted

class CommandLine( dict ):
	def __init__( self, argv=None, dashes=2 ):
		self.__args = { 'p' : [], 'k' : [] }
		self.__dashes = tuple( dashes ) if isinstance( dashes, ( tuple, list ) ) else ( dashes, )
		self.__schema = []
		self.__used = []
		self.opts = Bunch()
		if isinstance( argv, str ): argv = shlex.split( argv )
		elif argv is None: argv = getattr( sys, 'argv', [] )[ 1: ]
		for arg in argv: self.__args[ self._ArgType( arg ) ].append( arg )
	dashes = property( lambda self: self.__dashes )
	def _ArgType( self, arg ):
		if not isinstance( arg, str ): return 'p'
		allowableDashes = self.__dashes
		stripped = arg.lstrip( '-' )
		nDashes = len( arg ) - len( stripped )
		leadingAlpha = len( stripped ) and stripped[ 0 ].lower() in 'abcdefghijklmnopqrstuvwxyz'
		if 0 in allowableDashes and leadingAlpha and '=' in arg: return 'k' # note that this excludes anything that starts with a quote
		elif nDashes and nDashes in allowableDashes and leadingAlpha: return 'k'
		else: return 'p'
	def Option( self, name, default=Unspecified, container=Unspecified, **kwargs ):
		schema = self.__schema
		opt = OptionSchema( len( schema ), self.__dashes, name=name, default=default, **kwargs )
		schema.append( opt )
		if container is Unspecified: container = self.opts
		sources, value = opt.Resolve( self.__args[ 'p' ], self.__args[ 'k' ], container )
		self.__used += sources
		return value
	def Finalize( self ):
		for arg in self.__args[ 'k' ]:
			if arg not in self.__used: raise CommandLineError( 'could not interpret command-line argument %r (unrecognized option %s)' % ( arg, arg.split( '=', 1 )[ 0 ] ) )
		for index, arg in enumerate( self.__args[ 'p' ] ):
			if index not in self.__used: raise CommandLineError( 'unexpected argument %r' % ( arg ) )
		return self
	def Release( self ):
		self.opts.release()

if __name__ == '__main__':
	
	cmdline = CommandLine() # sys.argv[ 1: ] is the default
	cmdline.Option( 'width',    default=None, position=0, type=( None, int ), min=1 )
	cmdline.Option( 'height',   default=None, position=1, type=( None, int ), min=1 )
	cmdline.Option( 'size',     default=None, type=( None, int, tuple, list ), minlength=2, maxlength=2 )
	cmdline.Option( 'threaded', default=True, type=bool )
	cmdline.Option( 'backend',  default=None, type=( None, str ), values=[ None, 'pyglet', 'pygame', 'default', 'glfw', 'accel', 'shadylib' ], allowPartial=True, caseSensitive=False )
	cmdline.Finalize()
	print( cmdline.opts )
