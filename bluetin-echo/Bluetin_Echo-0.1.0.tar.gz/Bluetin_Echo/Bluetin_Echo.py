# Copyright (c) 2018 Mark A Heywood
# Author: Mark A Heywood
# https://www.bluetin.io/
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import time
import RPi.GPIO as GPIO

class Echo(object):
	# Use over 50ms measurement cycle. 
	def __init__(self, trigger_pin, echo_pin, mtrs_per_sec = 340):
		self._trigger_pin = trigger_pin
		self._echo_pin = echo_pin
		self._mtrs_per_sec = mtrs_per_sec
		self._cycling_delay = 0.05
		self._last_read_time = 0
		self._last_read = 0
		self._start()
		
	def _start(self):
		# Use Broadcom (BCM) pin numbering for the GPIO pins.
		GPIO.setmode(GPIO.BCM)
		# Configure Pins
		# Set Trigger pin as output
		GPIO.setup(self._trigger_pin, GPIO.OUT)
		# Set Echo pin as input
		GPIO.setup(self._echo_pin, GPIO.IN)      
		# Set trigger pin to false state
		GPIO.output(self._trigger_pin, False)
		self._last_read_time = time.time()
		# Add delay to stabelise sensor before first read
		time.sleep(0.5)
		# Trigger 10us pulse for initial cycling
		GPIO.output(self._trigger_pin, True)
		time.sleep(0.00001)
		GPIO.output(self._trigger_pin, False)
	
	def read(self, unit, samples = 1):
		if samples == 1:
			return self._read(unit)
		
		samplesTotal = 0
		if samples > 1:
			for sample in range(0, samples):
				samplesTotal += self._read(unit)
				time.sleep(self._cycling_delay)
				# print('Samples - ', samplesTotal)

			return (samplesTotal / samples)
		
	def _read(self, unit):
		# Check if enough time has passed before triggering device.
		if (time.time() - self._last_read_time) > self._cycling_delay:
			self._last_read_time = time.time()
			# Trigger 10us pulse
			GPIO.output(self._trigger_pin, True)
			time.sleep(0.00001)
			GPIO.output(self._trigger_pin, False)
			timeout = False
			# Get most recent time before pin rises
			echoStart = 0.0
			while GPIO.input(self._echo_pin) == 0:
				echoStart = time.time()
				# Prevent infinite loops, add timeout
				if (time.time() - self._last_read_time) > 0.06:
					timeout = True
					break

			# Get most recent time before pin falls
			echoStop = 0.0
			while GPIO.input(self._echo_pin) == 1:
				echoStop = time.time()
				# Prevent infinite loops, add timeout
				if (time.time() - self._last_read_time) > 0.06:
					timeout = True
					break

			if timeout == True:
				# Use last reading
				echoTime = self._last_read
			else:
				# Calculate pulse length
				echoTime = echoStop - echoStart

		else:
			# Device not rested enough, use last value.
			echoTime = self._last_read
			
		#print(echoTime)
		# Speed of sound = 343 m/s in 20 degrees C dry air
		# or 1,087 ft/s
		if unit == 'mm':
			# return mm
			distance = (echoTime * self._mtrs_per_sec * 1000) / 2
		elif unit == 'cm':
			# return cm
			distance = (echoTime * self._mtrs_per_sec * 100) / 2
		elif unit == 'inch':
			# return inch
			distance = (echoTime * self._mtrs_per_sec * 39.3701) / 2
		else:
			print('incorrect unit given')
			distance = 0
		
		self._last_read = echoTime
		# Return reading
		return distance
		
	def stop(self):
		# Reset GPIO settings
		GPIO.cleanup()

	@property
	def speed_of_sound(self):
		return self._mtrs_per_sec
	
	@speed_of_sound.setter
	def speed_of_sound(self, sos):
		self._mtrs_per_sec = sos

	@property
	def cycling_delay(self):
		return self._cycling_delay
	
	@cycling_delay.setter
	def cycling_delay(self, sDelay):
		self._cycling_delay = sDelay
