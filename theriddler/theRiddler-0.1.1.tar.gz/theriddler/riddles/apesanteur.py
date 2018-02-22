# Riddle 3: Apesanteur
from riddles.riddle import Riddle

class Apesanteur(Riddle):
	
	def __init__(self):
		self.description = 'Find the right Python module...Ask for help!'
		self.hint = 'Let Python list all available modules for you.\nLook for "fancy" modules.\n"Enter any module name to get more help."'
		self.path += "apesanteur\\"
		self.file_path = self.get_path("cool_stuff.txt")
		self.photo_path = self.get_path("flying.jpg")
		self.status_phrases ={
			'Python': "UPPERCASE and exclamation mark, please.", 
			'python': "UPPERCASE PLEASE. and exclamation mark.",
			'PYTHON': "Try an exclamation mark.", 
			'python': "UPPERCASE PLEASE. and exclamation mark.",
			'Python!': "UPPERCASE.", 
			'python!': "UPPERCASE PLEASE.",
			'antigravity': "Yes...not the right place to type this in.", 
			'Antigravity': "Yes...not the right place to type this in.",
			}
		self.solution = 'PYTHON!'
		self.topic = 'Python Interactive Shell'