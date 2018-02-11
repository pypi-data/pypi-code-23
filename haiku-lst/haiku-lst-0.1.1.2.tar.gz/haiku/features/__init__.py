import os
from . import selectors
from .analyzers import DefaultAnalyzer
import functools, operator
import pickle, shutil
import re

class Features:
	def __init__ (self, name, analyzer = None):
		self.name = name
		self.analyzer = analyzer or DefaultAnalyzer ()
		self.docs = []
		self.labels = {}
		self.terms = {}
		self.labterms = {}
		self.features = []
		self.original_terms = 0
	
	def filter (self, doc):
		return self.analyzer.analyze (doc)
			
	def add_document (self, label, doc):
		l = []
		terms = {}
		for tok in self.analyzer.analyze (doc):
			if not tok: 
				continue
			l.append (tok)
			try:
				terms [tok] += 1
			except KeyError:	
				terms [tok] = 1				
		if not l: return
		
		try:
			self.labels [label] += 1
		except KeyError:
			self.labels [label] = 1
			
		self.docs.append ((label, l))
		
		for tok, tf in terms.items ():			
			try:
				self.terms [tok] += 1
			except KeyError:
				self.terms [tok] = 1
			if label not in self.labterms:
				self.labterms [label] = {}
			if tok not in self.labterms [label]:
				self.labterms [label][tok] = (0, 0)
			freq, appr = self.labterms [label][tok]
			self.labterms [label][tok] = (freq + tf, appr + 1)			
	
	def reset_model (self):
		model_path = self.name
		if os.path.isdir (model_path):
			shutil.rmtree(model_path)				
		os.mkdir (model_path)
				
	def select (self, data, mindf = 0, maxdf = 0, top = 0, meth = 'oddsratio'):			
		for label, doc in data:
			self.add_document (label, doc)
		self.original_terms = len (self.terms)
			
		self.reset_model ()
		print ('labes: %d' % len (self.labels))
		print ('initial features: %d' % len (self.terms))
		valids = {}
		for tok, tf in self.terms.items ():
			if mindf and tf < mindf:
				continue
			if maxdf and tf > maxdf:
				continue
			valids [tok] = tf			
		self.terms = valids
		print ('pruned features: %d' % len (self.terms))
		
		labels = list (self.labels.keys ())
		labels.sort ()		
		tokenCount = []
		docCount = []
		for label in labels:
			docCount.append (self.labels [label])
			tokenCount.append (functools.reduce (operator.add, map (lambda x: x[1], self.labterms [label].values ())))
		
		selector = getattr (selectors, meth) (
			tokenCount, 
			docCount,
			functools.reduce (operator.add, self.terms.values ()), 
			len (self.docs), 
			len (self.labels)
		)		
		features = []
		for tok in self.terms:
			if tok not in self.terms: 
				continue
			stat = []
			for label in labels:
				try: 
					stat.append (self.labterms [label][tok])
				except KeyError:
					stat.append ((0, 0))
			val = selector.compute (stat)	
			features.append ((tok, val))

		features.sort (key = lambda x: x [1], reverse = 1)
		features = [x [0] for x in features]
		
		if top: 
			if top < 1:
				top = int (len (features) * top)
			features = features [:top]
			print ('cacluated features: %d' % len (features))				
		self.features = features
		self.save ()
		
		l = []
		cc = 0
		while 1:
			cc += 1
			try: 
				label, doc = self.docs.pop (0)
			except IndexError:
				break
			if cc % 100 == 0:	
				print (label, [tok for tok in doc if tok in self.features])	
			l.append ((label, [tok for tok in doc if tok in self.features]))
		return l
		
	def save (self):	
		base = os.path.join (self.name, 'features')
		os.mkdir (base)
		pickle.dump (self.features, open(os.path.join (base, 'features.pickle'),'wb'), -1)
	
	def load (self):
		fn = os.path.join (self.name, 'features', 'features.pickle')
		if not os.path.isfile (fn):
			return
		self.features = pickle.load(open(fn, 'rb'))		
