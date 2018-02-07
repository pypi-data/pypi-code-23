from .resolvable import Resolvable
import sys
from .input_grabbers import out_input, err_input


class UserInput( Resolvable):
	'''
        Lets a user input a string at a prompt.

	On resolution this will return a string.

	If no default is specified the prompt will repeat until the user 
	enters a string.

	'''

	def __init__(self, prompt, default=None, type=str, fineControlOnly=False):
		super(UserInput, self).__init__()
		self.prompt = prompt
		self.default = default
		self.type = type
		self.fineOnly = fineControlOnly

	def _resolve(self, useDefaults, fineControl):
		if useDefaults or (self.fineOnly and not fineControl):
			if self.default is None:
				raise UserInputError('No default.')
			return str(self.default)
		try_again = True
		while try_again:
			if self.default is None:
				inp = out_input(self.prompt + ': ')
			else:
				inp = out_input(self.prompt + ' [{}]: '.format(self.default))
			try_again = False
			if not inp: # use the default
				if self.default is not None:
					inp = self.default
					break
			try:
				self.type( inp) # we don't actually want to convert. We just want to make sure it's possible
			except ValueError:
				sys.stdout.write("Input must be of type '{}'".format(self.type))
				inp = None
				try_again = True
		
		return str(inp) # We want to treat defaults that aren't strings nicely

	
