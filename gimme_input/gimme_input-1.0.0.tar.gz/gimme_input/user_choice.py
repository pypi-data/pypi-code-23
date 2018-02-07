from .resolvable import Resolvable
import sys

class UserChoice(Resolvable):
	'''
	Let a user pick a choice from a set of options.

	On resolution this will return a single element.

	'new' may be assigned to a function that will be called
	if the user selects new. This can allow subwizards that create new 
	choices. The result of new() is automatically returned.
	'''
	def __init__(self, name, options, new=None, fineControlOnly=False):
		super(UserChoice, self).__init__()
		self.name = name
		self.opts = [el for el in options]
		self.fineOnly=fineControlOnly
		self.new = new
		
	def _resolve(self, useDefaults, fineControl):
		if ((len(self.opts) == 1 and not self.new) 
			or useDefaults 
			or (self.fineOnly and not fineControl)):
			return self.opts[0]

		elif len(self.opts) == 0 and not self.new:
			sys.stdout.write('No options for {} found.\n'.format(self.name))
			raise UserInputError('No options.')
			
		sys.stdout.write('\tPlease select an option for {}:\n'.format(self.name))
		for i, opt in enumerate(self.opts):
			sys.stdout.write('\t\t[{}] {}\n'.format(i, opt))
		if self.new:
			sys.stdout.write('\t\t[{}] Pick new\n'.format(len(self.opts)))
		choice = out_input('\tPlease enter the index of your choice [0]: ')
		try:
			choice = int(choice)
		except ValueError:
			choice = 0

		if choice == len(self.opts):
			return self.new()

		sys.stdout.write('Chose: {}\n'.format(self.opts[choice]))
		return self.opts[choice] 
