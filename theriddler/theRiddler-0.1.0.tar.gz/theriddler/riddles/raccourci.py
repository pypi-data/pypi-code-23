# Riddle 2: Raccourci
from riddles.riddle import Riddle

class Raccourci(Riddle):
	
	def __init__(self, active_frame=None):# "active_frame=None" for if no frame is given.
		self.description = 'The journey is the reward'
		self.hint = 'The way is the goal.\nThe "path" is the goal.\n...\nThe solution is the command you need to reach the complete directory you put the file in?\nDoes this even help.'
		self.path += "raccourci\\"
		self.file_path = self.get_path("starwars.txt")
		self.photo_path = self.get_path("put_me_somewhere.jpg")
		self.status_phrases ={
			'cd ': "You will have to download the file first, but it's a good approach.", 
			'cd': "You will have to download the file first, but it's a good approach."
			}
		self.solution = None# self.solution must be defined before use for initiation.
		self.active_frame = active_frame	
		self.topic = 'Command Line'
		
		
		# self.solution will depend on the directory selected for the download (see below).
		# it's buggy: a directory must be selected each time the app starts to generate the solution to this riddle.
		# also, once the keyword has been generated, it can not be typed in when other riddles are active and
		# displayed, as the the workaround in check_key() from the "Guard" class will only apply if the active_riddle 
		# is "Raccourci".
		try:
			path_input = str(self.active_frame.get_chosen_path())# tries to convert chosen_path from MainGUI to a string
			
			if path_input != "None" and path_input != "":
				self.solution = "cd " + path_input
				
				to_remove = '"/\\ '
				for char in to_remove:
					self.solution = self.solution.replace(char, "")
				
				print(self.solution)# test, TODO:remove		
		except:
			pass