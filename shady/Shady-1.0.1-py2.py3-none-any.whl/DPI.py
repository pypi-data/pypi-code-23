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
	'SetDPIAwareness',
	'GetDPIAwareness',
]

import ctypes, sys

def GetDPIAwareness():
	if sys.platform.lower().startswith( 'win' ):
		awareness = ctypes.c_int()
		try: func = ctypes.windll.shcore.GetProcessDpiAwareness
		except: return None
		func( 0, ctypes.byref( awareness ) )
		return awareness.value
	
def SetDPIAwareness( target=2, verbose=False ):
	"""
	This function does nothing on non-Windows platforms (returns True,
	meaning "it's all good").
	
	On Windows, this function attempts to use the Windows API (via ctypes)
	to change the current process's "DPI awareness" flag to one of the
	following levels:
	
	0: I am not going to pretend to be DPI-aware: therefore, the operating
	   system will take over, and may scale my graphical output.
	1: I claim to be DPI aware, but will not claim to be committed to
	   continuous monitoring of potential changes in DPI scaling in future.
	   The OS will initially leave me alone (and things will be pixel-for-pixel)
	   but if screen resolution or scaling changes, then the OS may take over
	   again. (NB: this level may be the best we can achieve on Windows 7 or
	   Vista.)
	2: (default) I claim that I will be continuously DPI-aware throughout my 
	   whole lifetime, so the OS will leave me alone.  This is what we want to
	   aim for, for pixel-for-pixel control.
	
	The awareness level can only be successfully changed once per process lifetime,
	and this includes changes that the OS itself may make when it launches the,
	process, in response to an external .exe.manifest file or because of registry
	entries (created when you check "Disable DPI scaling" in the "Compatibility"
	tab of an .exe file's properties dialog).
	
	This function will return True if the awareness level was either successfully
	changed to, or is already at, the desired level.  It will return False if the
	process is not at, and cannot be switched to, the desired level.
	"""
	if not sys.platform.lower().startswith( 'win' ):
		return True
		
	error = None
	success = False
	awareness = ctypes.c_int()

	try:
		ctypes.windll.shcore.GetProcessDpiAwareness( 0, ctypes.byref( awareness ) )
	except:
		sys.stderr.write( 'could not call GetProcessDpiAwareness\n' )
	else:
		if verbose: print( 'before: %d' % awareness.value )

	try:
		error = ctypes.windll.shcore.SetProcessDpiAwareness( target ) # supposedly this is the Windows 8 and 10 way
	except:
		sys.stderr.write( 'could not call SetProcessDpiAwareness\n' )
		if target:
			try:
				success = ctypes.windll.user32.SetProcessDPIAware() # supposedly this is the Windows-7 way: outcome undefined on Windows 8+ although from preliminary try on Windows 10 it looks like it might be equivalent to target=1
			except:
				sys.stderr.write( 'could not call SetProcessDPIAware\n' )
			else:
				if not success: sys.stderr.write( 'SetProcessDPIAware call failed\n' )
	else:
		if verbose: print( 'target: %d' % target )
		success = not error
	try:
		ctypes.windll.shcore.GetProcessDpiAwareness( 0, ctypes.byref( awareness ) )
	except:
		sys.stderr.write( 'could not call GetProcessDpiAwareness\n' )
	else:
		if verbose: print( ' after: %d' % awareness.value )
		success = awareness.value == target
		
	if not success and error: 
		sys.stderr.write( 'SetProcessDpiAwareness error: 0x%08x\n' % ctypes.c_uint32( error ).value )
	return success
	
if __name__ == '__main__':
	import sys
	args = getattr( sys, 'argv', [] )[ 1: ]
	target = 2
	if args: target = int( args.pop( 0 ) )
	SetDPIAwareness( target, verbose=True )

