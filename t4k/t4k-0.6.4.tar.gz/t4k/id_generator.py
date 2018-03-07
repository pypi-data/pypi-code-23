import random
import hashlib

class UniqueIdGenerator():

	INCREMENTING_SALT = 0

	# Keep a local random number generator so it can be seeded without
	# affecting the random module's global state
	RNG = random.Random()

	def __init__(
		self,
		length=16,
		deterministic=True,
		seed=None,
	):
		# Validation
		if seed is not None and not isinstance(seed, int):
			raise ValueError(
				'UniqueIdGenerator: seed must be an int or None.'
			)
		if length < 0 or length > 16 or not isinstance(length, int):
			raise ValueError(
				'UniqueIdGenerator: length must be an int '
				'between 0 and 32.'
			)

		# Set the seed
		if seed is not None:
			self.RNG.seed(seed)
			self.INCREMENTING_SALT = seed

		# Register state variables locally
		self.deterministic = deterministic
		self.length = length

	def get_id(self, string=''):
		# Use system time to make hash non-deterministic (if desired)
		if not self.deterministic:
			string += '%f' % self.RNG.random()
		# Return the first `self.length` number of hash characters
		return hashlib.sha1(string).hexdigest()[:self.length]

	def get_ids(self, int_or_strings):
		# Resolve whether an int or strings were provided for the hashing
		if isinstance(int_or_strings):
			strings = ['' for i in range(int_or_strings)]
		else:
			strings = int_or_strings
		# Return a bunch of ids
		return [self.get_id(string) for string in strings]


ID_GENERATOR = UniqueIdGenerator(deterministic=False)
def get_id():
	return ID_GENERATOR.get_id()
