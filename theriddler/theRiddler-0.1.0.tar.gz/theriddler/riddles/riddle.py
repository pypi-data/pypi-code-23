# Riddle Template
import os

class Riddle(object):
	
	dir = os.path.dirname(os.path.abspath(__file__))
	path = dir.split("theriddler")[0] + r"\theriddler\data\\"
	
	def get_path(self, ending):
		return self.path + ending
	
	def get_description(self):
		return self.description
	
	def get_hint(self):
		return self.hint
		
	def get_photo_path(self):
		return self.photo_path
	
	def get_file_path(self):
		return self.file_path
		
	def get_solution(self):
		return self.solution
	
	def get_status_phrases(self):
		return self.status_phrases
			
	def get_topic(self):
		return self.topic