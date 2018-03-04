import pip
import sys

try:
	import pyqrcode as qr
except:
	pip.main(['install','pyqrcode'])
	import pyqrcode as qr
try:
	import png
except:
	pip.main(['install','pypng'])
	import png
try:
	import urllib3
except:
	pip.main(['install','urllib3'])
	import urllib3
try:
	import json
except:
	pip.main(['install','json'])
	import json
try:
	from IPython.display import Image, display
except:
	pip.main(['install','IPython'])
	from IPython.display import Image, display
try:
	import time
except:
	pip.main(['install','time'])
	import time	

###############################
# module global variables

http_path_base = "http://deepdescent.herokuapp.com/projects/"
deeplink_path_base = "deepdescent://projects"

###############################
# class to track hyperparams
# must be parameters on __main__ module in global scope

class HyperTrack:

	param_names = []

	def _track_hp(self,param):
		return self.get_variable_name(param)

	def parameters(self,params):
		self.param_names = [self._track_hp(param) for param in params]

	def update_hyperparams(self):
		value = lambda x: sys.modules['__main__'].__dict__[x]
		return {param: value(param) for param in self.param_names}

	def get_variable_name(self, *variable):
		if len(variable) != 1:
			raise Exception('len of variables inputed must be 1')
		try:
			main_module = sys.modules['__main__'].__dict__.items()
			return [k for k, v in main_module if v is variable[0]][0]
		except:
			raise Exception('hyperparam untrackable because not in __main__ module\'s global scope')

###############################
# class to connect and make requests

class Networking:

	def project_info(self, pid):
		http = urllib3.PoolManager()
		url = http_path_base + str(pid)
		headers = {'Content-Type': 'application/json'}
		response = http.urlopen('GET', url, headers=headers)
		return json.loads(response.data.decode('utf-8'))

	def post_create_project(self, name):
		http = urllib3.PoolManager()
		# response = http.urlopen('POST', http_path_base)
		paylod = json.dumps({'name':'name', 'metadata':{'finished': True,'timestamp': int(time.time())}})
		headers = {'Content-Type': 'application/json'}
		response = http.urlopen('POST', url, body=paylod, headers=headers)
		return json.loads(response.data.decode('utf-8'))

	def post_create_project(self):
		http = urllib3.PoolManager()
		response = http.urlopen('POST',http_path_base)
		return json.loads(response.data.decode('utf-8'))

	def post_create_session(self,pid, metadata):
		http = urllib3.PoolManager()
		url = http_path_base+str(pid)+"/sessions"
		paylod = json.dumps({'id':pid, 'metadata': metadata})
		headers = {'Content-Type': 'application/json'}
		response = http.urlopen('POST', url, body=paylod, headers=headers)
		return json.loads(response.data.decode('utf-8'))

	def post_update_session(self, pid, sid, metadata):
		http = urllib3.PoolManager()
		url = http_path_base+str(pid)+"/sessions/"+str(sid)+"/updates"
		paylod = json.dumps({'project_id':pid, 'session_id':sid, 'metadata':metadata})
		headers = {'Content-Type': 'application/json'}
		response = http.urlopen('POST', url, body=paylod, headers=headers)
		return json.loads(response.data.decode('utf-8'))

	def post_complete_iteration(self, pid, sid, params):
		http = urllib3.PoolManager()
		url = http_path_base+str(pid)+"/sessions/"+str(sid)
		paylod = json.dumps(params)
		headers = {'Content-Type': 'application/json'}
		response = http.urlopen('PUT', url, body=paylod, headers=headers)
		return json.loads(response.data.decode('utf-8'))

###############################
# class to connect and make requests

class Nnpush:
	"""Class for tracking neural networ

	Class for tracking models/hyperparmeters/loss data remotely from mobile device.

	Attributes:
		getInstance: get singleton instance of object.

	"""

	# Here will be the instance stored.
	__instance = None

	# internal instance variables
	_id = None
	_uuid = None
	_track = HyperTrack()
	_network = Networking()
	_last_session_id = 0
	_name = ""

	#MARK: Singleton Config

	@staticmethod
	def getInstance():
		""" Static access method. """
		if Nnpush.__instance == None:
			Nnpush()
		return Nnpush.__instance

	def __init__(self):
		""" Virtually private constructor. """
		if Nnpush.__instance != None:
			raise Exception("This class is a singleton!")
			return
		else:
			# self._fetch_uuid()
			Nnpush.__instance = self
			print("created")


	# MARK: Instance Methods
	def update_project_info(self, pid):
		response = self._network.project_info(pid)

		if response['name'] is None:
			print("Invalid project-id or network failure")
			return
		self._name = response['name']

	def update_latest_session_id(self, session_id):
		if session_id > self._last_session_id:
			self._last_session_id = session_id

	def output_connect_info(self):
		print("\ntoken: ",self._uuid)
		print("pid: ",self._id)
		print("name: ",self._name)

	def _fetch_uuid(self):
		if self._id != None:
			print("uuid already exists, so don't get a new one")
			self.output_connect_info()
			return
		response = self._network.post_create_project()
		self._name = response['name']
		self._uuid = response['code']
		self._id = response['id']
		self.output_connect_info()

	def qr_authenticate(self):
		deeplink_uuid = deeplink_path_base+"?code="+self._uuid
		test_code = qr.create(deeplink_uuid)
		test_code.png('nnpush_qr_code.png',scale=3)
		display(Image(filename='nnpush_qr_code.png'))

	def set_complete(self, sid):
		params = {"project_id": self._id, "session_id": sid, "completed": True }
		response = self._network.post_complete_iteration(self._id, sid, params)
		print(response)

	# storing finished project data on a new session, 
	# since there is no way to store information at project level currently.
	# this is always posted only highest session# associated with current project
	# seen so far. The user can create new sessions though and iterations beyond this
	# which if client only looks at highest session # on project, will cause the project
	# to seem to become "reopened" and return to an running state.
	def set_complete_project(self):
		blob = {'project_complete':True, 'timestamp':int(time.time())}
		response = self._network.post_create_session(self._id, blob)
		print(response)

	def start_iteration(self):
		blob = self._track.update_hyperparams()
		blob['__timestamp'] = int(time.time())
		response = self._network.post_create_session(self._id, blob)
		#print(response)
		return response['id']

	def start_iteration(self):
		blob = self._track.update_hyperparams()
		response = self._network.post_create_session(self._id, blob)
		#print(response)
		return response['id']

	def update_session(self, sid, loss):
		blob = {'loss':loss}
		response = self._network.post_update_session(self._id, sid, blob)
		#print(response)

###############################
# module level calls

def token_connect(token, pid):
	"""Connect library to existing project.
	
	Connect library to existing project using token and pid.

	Args:
		token: project token in format 00000000-0000-0000-0000-000000000000
		pid: project id, e.g. 5

	"""
	pusher = Nnpush.getInstance()
	pusher._uuid = token
	pusher._id = pid
	pusher.update_project_info(pid)
	pusher.output_connect_info()
	pusher.qr_authenticate()

def qr_connect():
	"""Create project and display QR code to scan from app to connect.
	
	Project will only be created one first call, subsequent `qr_connect`
	calls will return same project.

	Args:
		Saves QR code image to file and displays it in output if within
		a jupyer notebook. Project token and id are printed out as well.

	"""
	pusher = Nnpush.getInstance()
	pusher._fetch_uuid()
	pusher.qr_authenticate()

def track_hyperparameters(params):
	"""Keep track of live hyperparameters.
	
	Add array of variables to be tracked between iterations. If iterations
	are changed between iterations, the updated values are reflected.

	The hyperparameter variables must exist at the global level in the
	main module.

	Args:
		params: array of hyperparameter variables

	"""
	pusher = Nnpush.getInstance()
	tracker = pusher._track
	tracker.parameters(params)

def start_iteration():
	"""Create new iteration to send loss data to.

	On creation, current hyperparameters, if they are being tracked by
	`track_hyperparameters` function, will retrieve current variable
	values to be associated with this iteration at this point.

	Returns:
		returns session id for created iteration.
  
	"""
	pusher = Nnpush.getInstance()
	return pusher.start_iteration()

def update_iteration(sid, loss):
	"""Updates an iteration with loss data point.

	Loss is sent to be associated with an iteration represented by
	session id.

	This call does add some extra overhead to training and so should
	be used sparingly and probably not on every single data point
	otherwise training time may become unnecessarily increased.

	Args:
		sid: session id of iteration to update
		loss: loss data point to associate with iteration

	"""
	pusher = Nnpush.getInstance()
	pusher.update_latest_session_id(sid)
	pusher.update_session(sid, loss)

def complete_training(sid):
	"""Mark an iteration as completed.

	This will mark the iteration as having completed.

	This will also trigger a push notification notifying the paired
	device that the iteration is compelted.

	Args:
		sid: session id of iteration to update

	"""
	pusher = Nnpush.getInstance()
	pusher.set_complete(sid)

def complete_project():
	"""Mark a project as completed.

	This will mark the project as having completed.

	This will also trigger a push notification notifying the paired
	device that the project is compelted.

	"""
	pusher = Nnpush.getInstance()
	pusher.set_complete_project()	
