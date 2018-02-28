def get_bit_values(number, size=32):
	"""
	Get bit values as a list for a given number

	>>> get_bit_values(1) == [0]*31 + [1]
	True

	>>> get_bit_values(0xDEADBEEF)
	[1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, ..., 0, 1, 1, 1, 1]

	You may override the default word size of 32-bits to match your actual
	application.
	>>> get_bit_values(0x3, 2)
	[1, 1]

	>>> get_bit_values(0x3, 4)
	[0, 0, 1, 1]
	"""
	res = list(gen_bit_values(number))
	res.reverse()
	# 0-pad the most significant bit
	res = [0] * (size - len(res)) + res
	return res


def gen_bit_values(number):
	"""
	Return a zero or one for each bit of a numeric value up to the most
	significant 1 bit, beginning with the least significant bit.
	"""
	while number:
		yield number & 0x1
		number >>= 1
