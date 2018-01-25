import os
import tensorflow as tf
import time

__version__ = "0.1a31"

class Session:
	def __init__ (self, model_dir, tfconfig = None):
		self.model_dir = model_dir
		self.tfconfig = tfconfig
		self.graph = tf.Graph ()
		self.tfsess = tf.Session (config = tfconfig, graph = self.graph)
		
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
		self.output_map = {}
		for k, v in signature_def.inputs.items ():
			self.input_map [k] = (v.name, v.dtype, [dim.size for dim in v.tensor_shape.dim])		
		for k, v in signature_def.outputs.items ():
			self.output_map [k] = (v.name, v.dtype, [dim.size for dim in v.tensor_shape.dim])				
		
	def run (self, *args, **kargs):
		return self.tfsess.run (*args, **kargs)
		
	def close (self):
		self.tfsess.close ()
	
tfsess = {}
			
def load_model (alias, model_dir, tfconfig = None):
	global tfsess
	tfsess [alias] = Session (model_dir, tfconfig)
	
def close ():
	global tfsess
	for v in tfsee.values ():
		tfsess.close ()
	tfsess = {}
	