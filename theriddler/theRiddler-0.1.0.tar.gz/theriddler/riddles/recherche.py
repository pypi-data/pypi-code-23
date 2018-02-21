# Riddle 14: Recherche
from riddles.riddle import Riddle

class Recherche(Riddle):
	
	def __init__(self):
		self.description = 'Find my flaw'
		self.hint = "Now that You got the source code: DO NOT CHEAT!\n\nGo through the test scripts."
		self.path += "recherche\\"
		self.file_path = self.get_path("reST.url")
		self.photo_path = self.get_path("nose.jpg")
		self.status_phrases ={
				'pypirc': "...Make a point!"
			}
		self.solution = '.pypirc'
		self.topic = 'Testing'