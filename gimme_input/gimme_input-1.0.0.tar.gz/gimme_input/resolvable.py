

class Resolvable:

	def __init__(self):
		self.resolved = False
		self.resolved_val = None

	def resolve(self, useDefaults=False, fineControl=False):
		if self.resolved:
			return self.resolved_val

		res = self._resolve(useDefaults, fineControl)
		self.resolved_val = res
		self.resolved = True
		return res

	def _resolve(self, useDefaults, fineControl):
		raise NotImplementedError()