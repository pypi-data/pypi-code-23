import unicodedata, re, os, sys
from delune import standard_analyzer

if sys.version_info[0] >= 3:	
	def unicode(string, setting):
		return string

class DefaultAnalyzer:	
	def tokenize (self, text):		
		def foo(c):
			if ord(c)>127: return ''
			if c.isdigit() or c.isalpha(): return c
			else : return ' '

		text = unicodedata.normalize('NFD', unicode(text, 'utf-8')).lower()
		text = ''.join(map(foo,text))
		text = re.sub(r'([a-z])([0-9])', r'\1 \2', text)
		text = re.sub(r'([0-9])([a-z])', r'\1 \2', text)
		text = re.sub(r'\s+', r' ', text)
		return text.strip().split()

					
class StandardAnalyzer (standard_analyzer):
	def analyze (self, doc, lang = "en"):
		return standard_analyzer.stem (self, doc, lang)
		