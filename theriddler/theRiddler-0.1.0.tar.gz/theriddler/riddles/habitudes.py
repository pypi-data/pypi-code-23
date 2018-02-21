# Riddle 4: Habitudes
from riddles.riddle import Riddle

class Habitudes(Riddle):
	
	def __init__(self):
		self.description = 'Old and bad habits'
		self.hint = "This script is pretty messed up.\nFix it. Run it."
		self.path += "habitudes\\"
		self.file_path = self.get_path("broken_script.py")
		self.photo_path = self.get_path("bad_habits.jpg")
		self.status_phrases ={
			'type': "Incomplete. This is the second part",
			'his': "Incomplete. This is the first part",
			}
		self.solution = 'histype'
		self.topic = 'Syntax and Semantics'