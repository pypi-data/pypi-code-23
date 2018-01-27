import os
import tensorflow as tf
import time

__version__ = "0.1a32"

class Session:
	def __init__ (self, model_dir, tfconfig = None):
		self.model_dir = model_dir
		self.tfconfig = tfconfig
		self.graph = tf.Graph ()
		self.tfsess = tf.Session (config = tfconfig, graph = self.graph)
		self.activation = []
		with self.graph.as_default ():
			meta = tf.saved_model.loader.load (
				self.tfsess, 
				[tf.saved_model.tag_constants.SERVING], 
				model_dir
			)
			self.tfsess.run (tf.global_variables_initializer())
		
		self.signature_def_name, signature_def = meta.signature_def.popitem ()
		# self.signature_def_name: predict_sounds
		self.input_map = {}
		self.outputs = []
		for k, v in signature_def.inputs.items ():
			self.input_map [k] = (v.name, v.dtype, [dim.size for dim in v.tensor_shape.dim])		
		for k, v in signature_def.outputs.items ():
			self.outputs.append ((k, v.name, v.dtype, [dim.size for dim in v.tensor_shape.dim]))				
			self.activation.append (v.name)
		#{'scores': ('Sigmoid:0', 1, [-1, 60])}
			
	def run (self, **kargs):
		return self.tfsess.run (self.activation, **kargs)
		
	def close (self):
		self.tfsess.close ()
	
tfsess = {}
			
def load_model (alias, model_dir, tfconfig = None):
	global tfsess
	tfsess [alias] = Session (model_dir, tfconfig)
	
def close ():
	global tfsess
	for sess in tfsess.values ():
		sess.close ()
	tfsess = {}
		