# Riddle 10: Jeux
from riddles.riddle import Riddle

class Jeux(Riddle):
	
	def __init__(self):
		self.description = 'Get it together!!'
		self.hint = 'Learn how to import whole scripts.\n\nJust play a bit :-)\nNo hand out demanded this time.'
		self.path += "jeux\\"
		self.file_path = self.get_path("gtg.py")
		self.photo_path = self.get_path("space.jpg")
		self.status_phrases ={
			'Ed Hardy': "...No space.",
			'ed hardy': '...No space. And uppercase, I mean You wouldn\'t write "nike", would you?!',
			'edHardy': "...It's a bIG E!",
			'edhardy': "...How would You like it if someone molested your name by writing it in lowercase?",
			}
		self.solution = 'EdHardy'
		self.topic = 'Script Import'