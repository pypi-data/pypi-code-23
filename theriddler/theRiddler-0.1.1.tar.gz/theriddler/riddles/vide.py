# Riddle 13: Vide
from riddles.riddle import Riddle

class Vide(Riddle):
	
	def __init__(self):
		self.description = 'No playing around this time!\nSit down and learn how to make Python distributions.\nRead about the "setup.py" file, Distutils and Setuptools.\nFind out what the "__init__.py" file is good for.\n\nKeyword in "Hints".'
		self.hint = 'None.'
		self.path += "vide\\"
		self.file_path = self.get_path("gobackandlearnstuff.txt")
		self.photo_path = self.get_path("noriddle.png")
		self.status_phrases ={'None' : 'Yes. Add a point.',
			}
		self.solution = 'None.'
		self.topic = 'Distribution Basics'