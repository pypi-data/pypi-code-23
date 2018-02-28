from __future__ import absolute_import, division


class NormalizingAxisJoystick(object):
	def set_translate_method(self, normalize_axes):
		"""
		Set the method that will be called to normalize
		the values for analog axis.  This should be called by the
		constructor.
		"""
		choices = [self.translate_identity, self.translate_using_data_size]
		self.translate = choices[normalize_axes]

	def translate_using_data_size(self, value, axis):
		"""
		Normalizes analog data to [0,1] for unsigned data
		and [-0.5,0.5] for signed data.

		The data size represents size in bytes used to represent
		the range of values that might be supplied by the axis.
		"""
		data_size = self.get_data_size_for_axis(axis)
		data_bits = 8 * data_size
		return value / (2**data_bits - 1)

	def translate_identity(self, value, axis):
		"""
		A translation method that always returns the same value.
		"""
		return value

	def get_data_size_for_axis(self, axis):
		"""
		Return the data size in bytes represented by the
		given axis.

		i.e. thumbs are 16-bit values (2 bytes)
		triggers are 8-bit values (1 byte)
		all other values are assumed to also be 16-bit values
		"""
		return [2, 1][axis in ('left_trigger', 'right_trigger')]
