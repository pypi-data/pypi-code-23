#!/usr/bin/env python
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
import Shady.Text  # necessary to enable text/font-handling functionality

cmdline = Shady.WorldConstructorCommandLine( width=750, top=50 )
shell = cmdline.Option( 'shell', False, type=bool, container=None )
cmdline.Finalize()

TEXTS = [ Shady.Text.TEST, Shady.Text.TEST_UNICODE ]
FONTS = list( Shady.Text.FONTS )
def Cycle( lst, backwards=False ):
	if backwards: lst.insert( 0, lst.pop( -1 ) )
	else: lst.append( lst.pop( 0 ) )
	return lst[ -1 ]

w = Shady.World( **cmdline.opts )

instructions = w.Stimulus( text="""\
  L / C / R   left / center / right alignment
F / shift+F   cycle through system fonts
      B / I   toggle .text.bold / .text.italic where possible
          M   set .text.font = 'monaco'
          T   toggle between English and Sanskrit demo texts
          D   try to find a Devanagari font for the Sanskrit 
      - / +   increase / decrease .text.size
      [ / ]   increase / decrease .text.border
  up / down   increase / decrease .text.linespacing
          Y   toggle yellow .text.bg
          G   toggle green  .text.blockbg
 Q / escape   close window
""", xy=w.Place( -1, 1 ), anchor=( -1, 1 ) )
instructions.text.Set( size=20 )

sample = w.Stimulus( text=Cycle( TEXTS ) )

caption = w.Stimulus(
	text = lambda t: '' if not sample.text else '%s (%s)%s' % ( sample.text.font, sample.text.style, ( '' if sample.text.font_found else '\nnot available' ) ),
	xy = lambda t: sample.Place( 0, -1 ) - [ 0, 30 ],
	anchor = ( 0, 1 ),
)
caption.text.Set( align='center' )

def EventHandler( world, event ):
	if event.type == 'key_press':
		# Detect event.type in [ 'key_press', 'key_release' ] and examine event.key:
		#     - event.key allows easy case-insensitive matching (it's always lower case)
		#     - non-printing keystrokes (e.g. 'escape', 'up', 'down') are reported
		#     - have to be careful what you assume about international keyboard layouts
		#       e.g. the condition `event.key == '8' and 'shift' in event.modifiers`
		#       guarantees the '*' symbol on English layouts but not on many others
		#     - event is not auto-repeated when the key is held down
		cmd = event.key
		if   cmd in [ 'q', 'escape' ]: world.Close()
		elif cmd in [ 'up'   ]: sample.text.linespacing *= 1.1
		elif cmd in [ 'down' ]: sample.text.linespacing /= 1.1

	if event.type == 'text':
		# Detect a event.type == 'text' and examine event.text:
		#     - case sensitive
		#     - non-printing keystrokes cannot be detected
		#     - independent of keyboard layout (you get whatever symbol the user intended to type)
		#     - events are re-issued on auto-repeat when the key is held down
		cmd = event.text.lower()
		if   cmd in [ 'c' ]: sample.text.align = 'center'
		elif cmd in [ 'l' ]: sample.text.align = 'left'
		elif cmd in [ 'r' ]: sample.text.align = 'right'
		elif cmd in [ 'm' ]: sample.text.font = 'monaco'
		elif cmd in [ 'd' ]: sample.text.font = [ 'arial unicode', 'devanagari', 'nirmala' ] # whichever matches first
		elif cmd in [ 'f' ] and FONTS: sample.text.font = Cycle( FONTS, 'shift' in event.modifiers )
		elif cmd in [ 'b' ]: sample.text.bold = not sample.text.bold
		elif cmd in [ 'i' ]: sample.text.italic = not sample.text.italic
		elif cmd in [ 't' ]: sample.text = Cycle( TEXTS ) # this is a shorthand - could also say sample.text.string = Cycle( TEXTS )
		elif cmd in [ '-' ]:      sample.text.size /= 1.1   # .size is an alias for .lineHeightInPixels, so these lines will fail if
		elif cmd in [ '+', '=' ]: sample.text.size *= 1.1   # text size has most recently been controlled via .emWidthInPixels instead
		elif cmd in [ 'g' ]: sample.text.blockbg = None if sample.text.blockbg else ( 0, 0.7, 0 )
		elif cmd in [ 'y' ]: sample.text.bg = None if sample.text.bg else ( 0.7, 0.7, 0 )
		elif cmd in [ '[', ']' ]:
			sign = -1 if cmd in [ '[' ] else +1
			value = sample.text.border  # could be a scalar (proportion of line height) or tuple of absolute pixel widths (horizontal, vertical)
			try: len( value )
			except: sample.text.border = max( 0, value + sign * 0.1 )
			else:   sample.text.border = [ max( 0, pixels + sign * 10 ) for pixels in value ]
w.SetEventHandler( EventHandler )

Shady.AutoFinish( w, shell=shell )
