# Riddle 11: Secrets
from riddles.riddle import Riddle

class Secrets(Riddle):
	
	def __init__(self):
		self.description = 'Steganography'
		self.hint = 'The image you will need for this riddle is the handed out "bib.png".\nPixel(0, 0) is THE color.\n\nTake a look in the shown book for a first help.\nSorry.'
		self.path += "secrets\\"
		self.file_path = self.get_path("help.jpg")
		self.photo_path = self.get_path("manual.jpg")
		self.status_phrases ={
			'Distribution' : "Great! But a little d is mandatory here...(lololol)"
			}
		self.solution = 'distribution'
		self.topic = 'Toolkit Tkinter'