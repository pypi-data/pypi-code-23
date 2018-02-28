#!/usr/bin/env python

"""
Linux joystick support

borrowed from http://entitycrisis.blogspot.com/2008/02/pyglet-joystick.html
"""

from pyglet import event

from glob import glob
import struct
from select import select

import six

from jaraco.input import NormalizingAxisJoystick as NormalizingJS

# Linux only gives us axis numbers: translate these to meaningful
#  names (as found in the XINPUT_GAMEPAD structure)
axis_name_map = {
	0: 'l_thumb_x',
	1: 'l_thumb_y',
	2: 'left_trigger',
	3: 'r_thumb_x',
	4: 'r_thumb_y',
	5: 'right_trugger',
}


class Joystick(event.EventDispatcher, NormalizingJS):
	JS_EVENT_BUTTON = 0x01  # /* button pressed/released */
	JS_EVENT_AXIS = 0x02  # /* joystick moved */
	JS_EVENT_INIT = 0x80  # /* initial state of device */
	JS_EVENT = "IhBB"
	JS_EVENT_SIZE = struct.calcsize(JS_EVENT)

	def __init__(self, device, normalize_axes=True):
		"device is numeric index or full path"
		if isinstance(device, six.integer_types):
			device = '/dev/input/js%d' % device
		event.EventDispatcher.__init__(self)
		self.dev = open(device)
		self.set_translate_method(normalize_axes=True)

	@classmethod
	def enumerate_devices(self):
		js_devs = glob('/dev/input/js*')
		return [self.__class__(path) for path in js_devs]

	def dispatch_events(self):
		r, w, e = select([self.dev], [], [], 0)
		if self.dev not in r:
			return
		evt = self.dev.read(self.JS_EVENT_SIZE)
		time, value, type, number = struct.unpack(self.JS_EVENT, evt)
		evt = type & ~self.JS_EVENT_INIT
		if evt == self.JS_EVENT_AXIS:
			value = self.translate(value, number)
			axis = axis_name_map.get(number, number)
			self.dispatch_event('on_axis', axis, value)
		elif evt == self.JS_EVENT_BUTTON:
			self.dispatch_event('on_button', number, value == 1)

	def on_axis(self, axis, value):
		pass

	def on_button(self, button, pressed):
		pass


Joystick.register_event_type('on_axis')
Joystick.register_event_type('on_button')


if __name__ == "__main__":
	j = Joystick(0)

	@j.event
	def on_button(button, pressed):
		print('button', button, pressed)

	@j.event
	def on_axis(axis, value):
		print('axis', axis, value)

	while True:
		j.dispatch_events()
