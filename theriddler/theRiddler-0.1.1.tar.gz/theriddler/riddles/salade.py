# Riddle 5: Salade
from riddles.riddle import Riddle

class Salade(Riddle):
	
	def __init__(self):
		self.description = 'Think twice before solving this'
		self.hint = "None."
		self.path += "salade\\"
		self.file_path = self.get_path("gibberish.rst")
		self.photo_path = self.get_path("character_shift.jpg")
		self.status_phrases ={
			'jleehulvk.uvw' : 'Well done!! ..But leave out the ending, just process with the file name.'
			}
		self.solution = 'jleehulvk'
		self.topic = 'Data Processing'