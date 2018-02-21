# Riddle 8: Inverse
from riddles.riddle import Riddle

class Inverse(Riddle):
	
	def __init__(self):
		self.description = 'Create your very first own Python GUI <3'
		self.hint = 'Use Python\'s built-in Tkinter Toolkit.\n"Why does my tkinter image appear blank??"\nDisplay and turn the given image, then inspect it.'
		self.path += "inverse\\"
		self.file_path = self.get_path("bib.png")
		self.photo_path = self.get_path("upsidedown.png")
		self.status_phrases ={
			}
		self.solution = 'py2exe'
		self.topic = 'GUI Toolkit Tkinter'