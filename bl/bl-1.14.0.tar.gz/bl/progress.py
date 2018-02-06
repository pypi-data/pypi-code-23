
import inspect, os, sys, traceback
from time import time
from bl.dict import Dict
from bl.json import JSON

class Progress(JSON):
	"""tabulate progress statistics for given processes, and report the progress of those processes"""
	
	def __init__(self, fn=None, data=None, **params):
		# JSON.__init__() loads the stored progress data from the given .json file
		super().__init__(fn=fn, data=data, params=params)
		if self.data is None: self.data = Dict()
		self.current_times = Dict()					# start times for current stack processes.
		self.init_key = self.stack_key

	def start(self, key=None, **params):
		"""initialize process timing for the current stack"""
		self.params.update(**params)
		key = key or self.stack_key
		if key is not None:
			self.current_times[key] = time()

	def runtime(self, key):
		if self.data.get(key) is not None:
			return sum([v['runtime'] for v in self.data[key]]) / len(self.data[key])

	def runtimes(self):
		return Dict(**{key:self.runtime(key) for key in self.data.keys()})

	def report(self, fraction=None):
		"""report the total progress for the current stack, optionally given the local fraction completed.
		fraction=None: if given, used as the fraction of the local method so far completed.
		runtimes=None: if given, used as the expected runtimes for the current stack.
		"""
		r = Dict()
		local_key = self.stack_key
		if local_key is None: return {}
		runtimes = self.runtimes()
		for key in self.stack_keys:
			if self.current_times.get(key) is None: 
				self.start(key=key)
			runtime = runtimes.get(key) or self.runtime(key)
			if key == local_key and fraction is not None:
				r[key] = fraction
			elif runtime is not None:
				r[key] = (time() - self.current_times[key]) / runtime
		return r

	def finish(self):
		"""record the current stack process as finished"""
		self.report(fraction=1.0)
		key = self.stack_key
		if key is not None:
			if self.data.get(key) is None:
				self.data[key] = []
			start_time = self.current_times.get(key) or time()
			self.data[key].append(Dict(runtime=time()-start_time, **self.params))

	@property
	def stack_keys(self):
		key = self.stack_key
		if key is not None:
			l = self.stack_key.split(',')
		else:
			l = []
		return [','.join(l[:i]) for i in range(1, len(l)+1)]

	@property
	def stack_key(self):
		try:
			return ','.join(list(reversed([
				t.filename+':'+t.function for t in 
				[inspect.getframeinfo(i.frame) for i in inspect.stack()]
				if os.path.abspath(t.filename) != os.path.abspath(__file__)	# omit locations in this file
				and t.function != '<module>'
				and 'runpy.py' not in t.filename
			])))
		except:
			log.error(traceback.format_exc())
