import os
from .classifier import *
from .features import Features

class Haiku:
	def __init__ (self, name, classifier = 0, analyzer = None, extra_svm_files = []):
		self.name = name
		self.model = None
		self.features = None
		self.traindata = []
		
		if classifier == 0: 
			self.liblinear_arguments = '-s 4'
		elif classifier == 1:
			self.liblinear_arguments = '-s 3'
		elif classifier == 2:
			self.liblinear_arguments = '-s 1'
		elif classifier == 3:
			self.liblinear_arguments = '-s 7'
		self.analyzer = analyzer
		self.extra_svm_files = extra_svm_files	
	
	def close (self):
		self.analyzer.close ()
	
	def select (self, data, mindf = 0, maxdf = 0, top = 0, meth = 'oddsratio'):
		self.features = Features (self.name, self.analyzer)
		self.traindata = self.features.select (data, mindf, maxdf, top, meth)		
				
	def train (self, processor_options = 1, feature_option = 0, normalize = 1, grid = 0):
		data = self.traindata
		
		converter_arguments = ''
		grid_arguments      = str (grid)
		feature_arguments   = '' 
		liblinear_arguments = '' # default is -s 4
		feature = processor_options & 1
		converter_arguments = '-feature {0}'.format(feature)
		
		feature_arguments += ' -N ' + str (normalize)
		if feature_option == 0:
			feature_arguments += ' -D 1'
		elif feature_option == 1:
			feature_arguments += ' -D 0'
		elif feature_option == 2:
			feature_arguments += ' -D 0 -T 1'
		elif feature_option == 3:
			feature_arguments += ' -D 0 -T 1 -I 1'
		
		m, svm_file = train_text(self.name, data, converter_arguments=converter_arguments, grid_arguments=grid_arguments, feature_arguments=feature_arguments, train_arguments=self.liblinear_arguments, extra_svm_files = self.extra_svm_files)
		m.save(self.name)
	
	def load (self):		
		self.model = TextModel()
		self.model.load(self.name)
		self.features = Features (self.name, self.analyzer)
		self.features.load ()
		
	def test (self, data, output = "test-result"):
		output = os.path.join (self.name, output)
		self.load ()
		testset = [(label, self.features.filter (text)) for label, text in data]		
		predict_result = predict_text(self.name, testset, self.model, svm_file=None, predict_arguments = self.liblinear_arguments, extra_svm_files = self.extra_svm_files)	
		print("Accuracy = {0:.4f}% ({1}/{2})".format(
			predict_result.get_accuracy()*100, 
			sum(ty == py for ty, py in zip(predict_result.true_y, predict_result.predicted_y)),
			len(predict_result.true_y)))	
		predict_result.save(output, True)
		return predict_result.get_accuracy()
		
	def guess (self, text, default = None):		
		ftext = self.features.filter (text)
		if not ftext:
			return None
		return predict_single_text (
			ftext, 
			self.model, 
			self.liblinear_arguments, 
			self.extra_svm_files
		).predicted_y	
		
			
if __name__ == '__main__':
	
	model = Model ("unspsc", 0)
	model.train ("data/train_file")
	model.test ("data/test_file")
	
	
