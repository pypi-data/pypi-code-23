# -*- coding: utf-8 -*-
import re
import nltk


class Vectorizer(object):

	SPLITTING_PATTERN = re.compile(
		#r'(?:\s|!|,|—|\(|\)|\[|\]|<|>|\'|"|`|~|/|\\|\?|\||:|;|{|})+'
		r'(?:\s|!|,|—|\(|\)|\[|\]|<|>|"|`|~|\\|\?|\||;|{|})+'
	)
	TERMINAL_PUNCTUATION = r'\.|-|\''
	LEADING_PUNCTUATION = re.compile('^(' + TERMINAL_PUNCTUATION + ')*')
	TRAILING_PUNCTUATION = re.compile( '(' + TERMINAL_PUNCTUATION + ')*$')

	def __init__(self, do_lemmatize=True):
		self.vocab = {}
		self.lookup = []
		self.do_lemmatize = do_lemmatize
		self.lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()


	def get_size(self):
		return len(self.lookup)


	def add(self, token):
		token = self.clean(token)
		if token in self.vocab:
			raise ValueError(
				'The token "%s" is already in the vocabulary.' % token
			)

		self.vocab[token] = len(self.lookup)
		self.lookup.append(token)


	def add_doc(self, doc):
		tokens = self.SPLITTING_PATTERN.split(doc)
		for t in tokens:
			self.add(t)


	def clean(self, token):
		token = token.strip()

		if self.looks_like_url(token):
			return token

		token = self.LEADING_PUNCTUATION.sub('', token)
		token = self.TRAILING_PUNCTUATION.sub('', token)
		if self.do_lemmatize:
			token = self.lemmatizer.lemmatize(token)

		token = token.strip()

		return token


	def looks_like_url(self, token):
		return token.startswith('http')


	def code_to_token(self, code):
		try:
			return self.lookup[code]
		except IndexError:
			raise ValueError(
				'There is no entry in the vocabulary at code %d. '
				'The vocabulary size is only %d.' % (code, len(self.lookup))
			)


	def token_to_code(self, token):
		cleaned_token = self.clean(token)
		try:
			return self.vocab[cleaned_token]
		except KeyError:
			self.add(token)
			return self.vocab[cleaned_token]


	def doc_to_vec(self, doc):
		vec = {}
		tokens = self.SPLITTING_PATTERN.split(doc)
		for token in tokens:
			code = self.token_to_code(token)
			try:
				vec[code] += 1
			except KeyError:
				vec[code] = 1

		return vec





