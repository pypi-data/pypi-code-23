# Riddle 15: Progrès
from riddles.riddle import Riddle

class Progres(Riddle):
	
	def __init__(self):
		self.description = 'Your turn! Any ideas?\n\nGet yourself a partner and and fix me.\nRefactor me. Expand me.\nLeave your footprint!'
		self.hint = 'Read the docs first.\nTalk to each other, tastes are different.\nDO NOT forget to write tests.'
		self.path += "progres\\"
		self.file_path = self.get_path(".pypirc-surpriiiiise!")
		self.photo_path = self.get_path("diy.jpg")
		self.status_phrases ={
			}
		self.solution = 'executable'
		self.topic = 'Development'