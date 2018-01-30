import os
import tensorflow as tf
import time

__version__ = "0.1b2"

class Session:
	def __init__ (self, model_dir, tfconfig = None):
		self.model_dir = model_dir
		try:
			self.version = int (os.path.basename (model_dir))
		except:
			self.version = 0	
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
		
		self.signature_def_name, signature_def = meta.signature_def.popitem ()
		self.input_map = {}
		self.outputs = []
		for k, v in signature_def.inputs.items ():
			self.input_map [k] = (v.name, self.graph.get_tensor_by_name (v.name), v.dtype, [dim.size for dim in v.tensor_shape.dim])					
		for k, v in signature_def.outputs.items ():
			self.outputs.append ((k, v.name, self.graph.get_tensor_by_name (v.name), v.dtype, [dim.size for dim in v.tensor_shape.dim]))				
			self.activation.append (v.name)
				
	def get_version (self):
		return self.version
			
	def run (self, feed_dict):
		return self.tfsess.run (self.activation, feed_dict = feed_dict)
		
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
		