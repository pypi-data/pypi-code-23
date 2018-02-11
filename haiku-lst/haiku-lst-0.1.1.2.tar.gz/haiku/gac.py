from .haiku import Haiku
from .features import Features

"""
Examples:

ratio = 1.0
model_path = os.path.join (os.path.dirname (__file__), "unspsc")
test_set = [	
	(2, 0, 4000, haiku.FS_CF, haiku.CL_L2),
	(2, 0, 3000, haiku.FS_CF, haiku.CL_L2),
	(3, 0, 3000, haiku.FS_CF, haiku.CL_L2),
	(3, 0, 2000, haiku.FS_CF, haiku.CL_L2),
]
	
test_set = [	
	(2, 0, 4000, haiku.FS_CF, haiku.CL_L2)	
]
analyzer =  DeLuenAnalyzer (200, stem_level = 2, make_lower_case = 1)
#analyzer = TextAnalyzer (1, 1, 1)	

trainset = build_data ("http://home.skitai.com:5001/v1", 0)	
gac = GuessAndCheck (trainset, test_set, model_path, ratio, analyzer)
gac.runtest ()

#For commit,
gac.runtest (0)

"""

class GuessAndCheck:
	def __init__ (self, trainset, test_set, model_path, ratio = 0.8, analyzer = None):
		self.trainset = trainset
		self.test_set = test_set
		self.model_path = model_path
		self.ratio = ratio
		self.analyzer = analyzer
	
	def get_barrier (self):
		return int (len (self.trainset) * self.ratio)
		
	def train_and_test (self, ratio, option):	
		barrier = self.get_barrier ()
		print ("training %d data" % barrier)		
		# CS_L2, FT_BIN, BIGRAM
		classifier, featurerepr, processor = 2, 0, 1 
		params = option [4:]
		if len (params) == 3:
			classifier, featurerepr, processor = params
		elif len (params) == 2:
			classifier, featurerepr = params	
		else:
			classifier = params	[0]
		
		model = Haiku (self.model_path, classifier, self.analyzer)
		model.select (self.trainset [:barrier], *option [:4])		
		model.train (processor, featurerepr, normalize = 1, grid = 0)
		return model.features, model.test (self.trainset [(self.ratio == 1 and -1000 or barrier):])			
		
	def runtest (self, index = -1):
		results = []	
		for option in (index != -1 and [self.test_set [index]] or self.test_set):
			fe, accuracy = self.train_and_test (self.ratio, option)
			results.append (((accuracy, len (fe.labels), len (fe.features), fe.original_terms, len (fe.terms)), option))
			
		print ('------------------')
		print ('testing done.')
		print ('------------------')
		for acc, option in results:
			print ("%2.4f labels:%d, features: %d, terms: %d -> %d " % acc)
			print ("       options: %s" % str (option))
		print ()	
		
	