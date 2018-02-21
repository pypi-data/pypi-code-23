# Riddle 6: Rareté
from riddles.riddle import Riddle

class Rarete(Riddle):
	
	def __init__(self):
		self.description = 'Rare ones'
		self.hint = "No hints here either.\n\n\n...make a dict, count the chars."
		self.path += "rarete\\"
		self.file_path = self.get_path("mess.txt")
		self.photo_path = self.get_path("book.jpg")
		self.status_phrases ={
			'ualit': "hat's nice! But you probably missed some chara.",
			'qual': 'Nice match, in german even. I hope you don\'t think the same about "The Riddler"...',
			'Quality': "Please try again with lowercase."
			}
		self.solution = 'quality'
		self.topic = 'Data Processing'