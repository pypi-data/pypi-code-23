#!/usr/bin/env python

# $Id$

"""
Module for interfacing with the Microsoft XBox 360 controllers
via the XInput library.
"""

from __future__ import division

import ctypes
import sys
import time
from operator import itemgetter, attrgetter
from itertools import count, starmap

from pyglet import event

from ..base import NormalizingAxisJoystick as NormalizingJS
from ..binary import get_bit_values


class XINPUT_GAMEPAD(ctypes.Structure):
	_fields_ = [
		('buttons', ctypes.c_ushort),  # wButtons
		('left_trigger', ctypes.c_ubyte),  # bLeftTrigger
		('right_trigger', ctypes.c_ubyte),  # bLeftTrigger
		('l_thumb_x', ctypes.c_short),  # sThumbLX
		('l_thumb_y', ctypes.c_short),  # sThumbLY
		('r_thumb_x', ctypes.c_short),  # sThumbRx
		('r_thumb_y', ctypes.c_short),  # sThumbRy
	]


class XINPUT_STATE(ctypes.Structure):
	_fields_ = [
		('packet_number', ctypes.c_ulong),  # dwPacketNumber
		('gamepad', XINPUT_GAMEPAD),  # Gamepad
	]


# todo: is this the right DLL?  Should I also try others?
xinput = ctypes.windll.xinput9_1_0
# others I've encountered:
# xinput1_2, xinput1_1 (32-bit Vista SP1)
# xinput1_3 (64-bit Vista SP1)


def struct_dict(struct):
	"""
	take a ctypes.Structure and return its field/value pairs
	as a dict.

	>>> 'buttons' in struct_dict(XINPUT_GAMEPAD)
	True
	>>> struct_dict(XINPUT_GAMEPAD)['buttons'].__class__.__name__
	'CField'
	"""
	def get_pair(pair):
		field, type = pair
		return field, getattr(struct, field)
	return dict(map(get_pair, struct._fields_))


ERROR_DEVICE_NOT_CONNECTED = 1167
ERROR_SUCCESS = 0


class XInputJoystick(event.EventDispatcher, NormalizingJS):
	"""
	XInputJoystick

	A stateful wrapper, using pyglet event model, that binds to one
	XInput device and dispatches events when states change.

	Example:
	controller_one = XInputJoystick(0)
	"""
	max_devices = 4

	# axis fields are everything but the buttons
	axis_fields = dict(XINPUT_GAMEPAD._fields_)
	axis_fields.pop('buttons')

	def __init__(self, device_number, normalize_axes=True):
		values = vars()
		del values['self']
		self.__dict__.update(values)

		super(XInputJoystick, self).__init__()

		self._last_state = self.get_state()
		self.received_packets = 0
		self.missed_packets = 0

		self.set_translate_method(normalize_axes)

	def get_state(self):
		"Get the state of the controller represented by this object"
		state = XINPUT_STATE()
		res = xinput.XInputGetState(self.device_number, ctypes.byref(state))
		if res == ERROR_SUCCESS:
			return state
		if res != ERROR_DEVICE_NOT_CONNECTED:
			msg = (
				"Unknown error %d attempting to get state of device %d"
				% (res, self.device_number)
			)
			raise RuntimeError(msg)
		# else return None (device is not connected)

	def is_connected(self):
		return self._last_state is not None

	@staticmethod
	def enumerate_devices():
		"Returns the devices that are connected"
		devices = map(XInputJoystick, range(XInputJoystick.max_devices))
		return filter(lambda d: d.is_connected(), devices)

	def dispatch_events(self):
		"The main event loop for a joystick"
		state = self.get_state()
		if not state:
			raise RuntimeError("Joystick %d is not connected" % self.device_number)
		if state.packet_number != self._last_state.packet_number:
			# state has changed, handle the change
			self.update_packet_count(state)
			self.handle_changed_state(state)
		self._last_state = state

	def update_packet_count(self, state):
		"Keep track of received and missed packets for performance tuning"
		self.received_packets += 1
		missed_packets = state.packet_number - self._last_state.packet_number - 1
		if missed_packets:
			self.dispatch_event('on_missed_packet', missed_packets)
		self.missed_packets += missed_packets

	def handle_changed_state(self, state):
		"Dispatch various events as a result of the state changing"
		self.dispatch_event('on_state_changed', state)
		self.dispatch_axis_events(state)
		self.dispatch_button_events(state)

	def dispatch_axis_events(self, state):
		for axis in self.axis_fields:
			old_val = getattr(self._last_state.gamepad, axis)
			new_val = getattr(state.gamepad, axis)
			old_val = self.translate(old_val, axis)
			new_val = self.translate(new_val, axis)
			# todo: implement some tolerance and deadzones to dampen noise
			if old_val != new_val:
				self.dispatch_event('on_axis', axis, new_val)

	def get_data_size_for_axis(self, axis):
		"""
		Override get_data_size_for_axis for two reasons:
		1) This class passes axis names instead of numeric indices.
		2) Data size is determined from the actual structure.
		"""
		type = self.axis_fields[axis]
		return ctypes.sizeof(type)

	def dispatch_button_events(self, state):
		changed = state.gamepad.buttons ^ self._last_state.gamepad.buttons
		changed = get_bit_values(changed, 16)
		buttons_state = get_bit_values(state.gamepad.buttons, 16)
		changed.reverse()
		buttons_state.reverse()
		button_numbers = count(1)
		values = zip(changed, button_numbers, buttons_state)
		changed_buttons = filter(itemgetter(0), values)
		tuple(starmap(self.dispatch_button_event, changed_buttons))

	def dispatch_button_event(self, changed, number, pressed):
		self.dispatch_event('on_button', number, pressed)

	# stub methods for event handlers
	def on_state_changed(self, state):
		pass

	def on_axis(self, axis, value):
		pass

	def on_button(self, button, pressed):
		pass

	def on_missed_packet(self, number):
		pass


map(XInputJoystick.register_event_type, [
	'on_state_changed',
	'on_axis',
	'on_button',
	'on_missed_packet',
])


def determine_optimal_sample_rate(joystick=None):
	"""
	Poll the joystick slowly (beginning at 1 sample per second)
	and monitor the packet stream for missed packets, indicating
	that the sample rate is too slow to avoid missing packets.
	Missed packets will translate to a lost information about the
	joystick state.
	As missed packets are registered, increase the sample rate until
	the target reliability is reached.
	"""
	# in my experience, you want to probe at 200-2000Hz for optimal
	#  performance
	if joystick is None:
		joystick = XInputJoystick.enumerate_devices()[0]

	j = joystick

	print(
		"Move the joystick or generate button events characteristic of your app")
	print("Hit Ctrl-C or press button 6 (<, Back) to quit.")

	# here I use the joystick object to store some state data that
	#  would otherwise not be in scope in the event handlers

	# begin at 1Hz and work up until missed messages are eliminated
	j.probe_frequency = 1  # Hz
	j.quit = False
	j.target_reliability = .99  # okay to lose 1 in 100 messages

	@j.event
	def on_button(button, pressed):
		# flag the process to quit if the < button ('back') is pressed.
		j.quit = (button == 6 and pressed)

	@j.event
	def on_missed_packet(number):
		print('missed %(number)d packets' % vars())
		total = j.received_packets + j.missed_packets
		reliability = j.received_packets / float(total)
		if reliability < j.target_reliability:
			j.missed_packets = j.received_packets = 0
			j.probe_frequency *= 1.5

	while not j.quit:
		j.dispatch_events()
		time.sleep(1 / j.probe_frequency)
	print("final probe frequency was %s Hz" % j.probe_frequency)


def sample_first_joystick():
	"""
	Attempt to connect to the first available controller and monitor
	its output, logging changes to the screen
	"""
	joysticks = XInputJoystick.enumerate_devices()
	device_numbers = map(attrgetter('device_number'), joysticks)

	print('found %d devices: %s' % (len(joysticks), device_numbers))

	if not joysticks:
		sys.exit(0)

	j = joysticks[0]
	print('using %d' % j.device_number)

	@j.event
	def on_button(button, pressed):
		print('button', button, pressed)

	@j.event
	def on_axis(axis, value):
		print('axis', axis, value)

	# @j.event
	# def on_state_changed(state):
	# 	print('state has changed', state.packet_number)
	# 	print(struct_dict(state.gamepad))

	# @j.event
	# def on_missed_packet(number):
	# 	print('missed %(number)d packets' % vars())

	while True:
		j.dispatch_events()
		time.sleep(.01)


if __name__ == "__main__":
	sample_first_joystick()
	# determine_optimal_sample_rate()
