from os import path
import os
import threading
from .haiku import Haiku
from .gac import GuessAndCheck
from .features import Features
from .features.analyzers import DefaultAnalyzer, StandardAnalyzer

__version__ = "0.1.1.1"

UNIGRAM = 0
BIGRAM = 1

FT_BIN = 0
FT_WC = 1
FT_TF = 2
FT_TFIDF = 3

CL_CS = 0
CL_L1 = 1
CL_L2 = 2
CL_LR = 3

FS_MI = "mutual_information"
FS_CHI2 = "chi2statistics"
FS_DICE = "dice_coefficient"
FS_JACCARD = "jaccard_coefficient"
FS_CF = "category_frequency"	
FS_DF = "document_frequency"
FS_OR = "oddsratio"
FS_FLOG = "freqlogp"
FS_IG = "information_gain"


class Models:
	def __init__ (self):
		self.d = {}
		self.lock = threading.Lock ()
		
	def add (self, alias, model):
		model.load ()
		with self.lock:
			self.d [alias] = model
	
	def get (self, alias):
		with self.lock:
			return self.d.get (alias)
	
	def names (self):
		return list (self.d.keys ())			
	
	def close (self):
		for k, v in self.d.items ():
			v.close ()
			
models = Models ()
		

__doc__ = """
Preprocessor options. The options include stopwrod removal, stemming, and bigram. (default 1)
0   no stopword removal, no stemming, unigram
1   no stopword removal, no stemming, bigram
2   no stopword removal, stemming, unigram
3   no stopword removal, stemming, bigram
4   stopword removal, no stemming, unigram
5   stopword removal, no stemming, bigram
6   stopword removal, stemming, unigram
7   stopword removal, stemming, bigram
    
Grid search for the penalty parameter in linear classifiers. (default 0)
0   disable grid search (faster)
1   enable grid search (slightly better results)

Feature representation. (default 0)
0   binary feature
1   word count 
2   term frequency
3   TF-IDF (term frequency + IDF)

Instance-wise normalization before training/test (default 1)
0
1

Classifier. (default 0)
0   support vector classification by Crammer and Singer
1   L1-loss support vector classification
2   L2-loss support vector classification
3   logistic regression

Append extra libsvm-format data. This parameter can be applied many 
times if more than one extra svm-format data set need to be appended.

"""
