from skitai.saddle import Saddle
import tfserver
import tensorflow as tf
from tfserver import prediction_service_pb2, predict_pb2
from tensorflow.python.framework import tensor_util
import numpy as np
import os

app = Saddle (__name__)
app.debug = True
app.use_reloader = True

app.access_control_allow_origin = ["*"]
	
@app.before_mount
def before_mount (wasc):
	for alias, params in app.config.tf_models.items ():
		config = None
		if isinstance (params, str):
			model_dir = params
		elif len (params) == 1:
			model_dir = params [0] 
		else:
			model_dir, config = params
		wasc.logger ("app", "serve tensorflow model '{}' on {}".format (alias, model_dir), 'info')	
		tfserver.load_model (alias, model_dir, config)
	
@app.route ("/tensorflow.serving.PredictionService/Predict")
def Predict (was, request, timeout = 10):	
	sess = tfserver.tfsess.get (request.model_spec.name)
	
	feed_dict = {}
	for k, v in request.inputs.items ():
		tensor_name, tensor, dtype, shape = sess.input_map [k]
		feed_dict [tensor] = tensor_util.MakeNdarray (v)
	predict_results = sess.run (feed_dict)
	
	response = predict_pb2.PredictResponse()
	for i, result in enumerate (sess.outputs):
		predict_result = predict_results [i]		
		response.outputs [sess.outputs [i][0]].CopyFrom (
			tensor_util.make_tensor_proto(predict_result.astype("float32"), shape=predict_result.shape)
		)
	return response
	
@app.route ("/predict")
def predict (was, **inputs):
	sess = tfserver.tfsess.get (request.model_spec.name)
	
	feed_dict = {}
	for k, v in inputs.items ():
		tensor_name, tensor, dtype, shape = sess.input_map [k]
		feed_dict [tensor] = np.array (v)		
	predict_results = sess.run (feed_dict = feed_dict)
	
	response = {}
	for i, result in enumerate (sess.outputs):
		predict_result = predict_results [i]		
		response [sess.outputs [i][0]] = predict_result.astype ("float32").tolist ()		
	return was.response.api (response)

@app.route ("/<model>/version/")
def version (was, model):	
	sess = tfserver.tfsess.get (model)
	if sess is None:
		return was.response ("404 Not Found")
	return was.response.api (version = sess.get_version ())



	