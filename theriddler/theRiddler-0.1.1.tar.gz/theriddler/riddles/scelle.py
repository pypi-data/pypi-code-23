# Riddle 9: Scellé
from riddles.riddle import Riddle

# imports for "show_amount()"
import certifi
import urllib3
from bs4 import BeautifulSoup
import re

# At first, the idea was to create an encrypted ZIP file. The password then would have 
# been set to the amount of "HTWG" strings found within the website's source code. 
# Python comes with a built-in "zipfile" module, which provides tools to create, read, 
# write, append, and list a ZIP file. 
# Unfortunately, it seems that there are by now (02.2018) very few and unpleasant
# possibilities for creating encrypted(!) ZIP(or RAR) files in Python 3.X, so a 
# workaround was made by throwing a dialog window before the Download Button to 
# ask for the amount. 

class Scelle(Riddle):

	def __init__(self):
		self.description = 'How much "HTWG" is in there?'
		self.hint = 'MAYBE you should take a look in the source.\nFind a way to access the the homepage\'s data.\n\nRead about Python\'s built-in "zipfile" module.\nRemember the hint I gave you last riddle?\n..You should.'
		self.path += "scelle\\"
		self.file_path = self.get_path("locked.zip")
		self.photo_path = self.get_path("htwg_website.jpg")
		self.status_phrases ={
			'H': "This is NOT the password of the riddle",
			'fooled': "Right! ..Try in uppercase.",
			}
		self.solution = 'FOOLED'
		self.topic = 'I/O'

	def get_amount(self):
		"""returns the amount of "HTWG" strings found within the source code of the HTWG homepage."""
		try:
			http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
			url = "https://www.htwg-konstanz.de/"
			response = http.request('GET', url)# access to the htwg website.
			soup = BeautifulSoup(response.data.decode('utf-8'), "html.parser")# read websites's source code.
			search = re.findall(r"HTWG", soup.prettify())# search source code for "HTWG" strings.
			amount_of_strings = 0
			for match in search:
				amount_of_strings += 1
			return str(amount_of_strings)
		except:
			return False