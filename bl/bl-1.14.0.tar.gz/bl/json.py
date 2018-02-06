
import os, json
from bl.file import File

class JSON(File):
	
	def __init__(self, fn=None, data=None, **params):
		super().__init__(fn=fn, data=data, **params)
		if self.data is None and self.fn is not None and os.path.exists(self.fn):
			self.data = self.read()
		if self.data is not None:
			if type(self.data)==bytes:
				self.data = self.data.decode('utf-8')
			if type(self.data)==str:
				self.data = json.loads(self.data)

	def write(self, fn=None, data=None, indent=2):
		fn = fn or self.fn
		data = data or self.data
		if type(data) == bytes:
			d = data
		elif type(data) == str:
			d = data.encode('utf-8')
		else:
			d = json.dumps(data, indent=2).encode('utf-8')
		super().write(fn=fn, data=d)
