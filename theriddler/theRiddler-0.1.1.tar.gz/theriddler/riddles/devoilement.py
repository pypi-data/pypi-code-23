# Riddle 12: Dévoilement
from riddles.riddle import Riddle

class Devoilement(Riddle):
	
	def __init__(self):
		self.description = 'Read me!'
		self.hint = 'Look for "theRiddler".\nDownload the package.\nGo through the files.'
		self.path += "devoilement\\"
		self.file_path = self.get_path("aid.url")
		self.photo_path = self.get_path("readme.jpg")
		self.status_phrases ={}
		self.solution = 'nextlvlpls'
		self.topic = 'PyPI Registration'