import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from shutil import copy2
from random import randint

# Testing
from nose.tools import *

# import Riddles
from riddles.bete import Bete
from riddles.raccourci import Raccourci
from riddles.interieur import Interieur
from riddles.habitudes import Habitudes
from riddles.salade import Salade
from riddles.rarete import Rarete
from riddles.motif import Motif
from riddles.inverse import Inverse
from riddles.scelle import Scelle
from riddles.jeux import Jeux
from riddles.secrets import Secrets
from riddles.devoilement import Devoilement
from riddles.vide import Vide
from riddles.recherche import Recherche
from riddles.progres import Progres
from riddles.enroulement import Enroulement
from riddles.apesanteur import Apesanteur
 
# Master Frame
class RiddlerGUI(tk.Tk):
	"""Master Frame"""	
	
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		
		project_dir = os.path.dirname(os.path.abspath(__file__)).split("theriddler")[0]
		path = project_dir + r"\theriddler\data\\"	
		self.iconbitmap(path + "brushed_r.ico")# changes the window bar icon(up left, instead of the tk feather symbol).
		
		self.geometry("600x650+10+10")
		self.resizable(width=False, height=False)
		self.title("the RIDDLER")
		self.configure(background="red4")
		
		master = tk.Frame(self)
		master.pack(side="top", fill = "both", expand= True)
		master.grid_rowconfigure(0, weight=1)
		master.grid_columnconfigure(0, weight=1)
		
		# Statusbar
		self._job = None# timer state variable
		
		self.status_var = tk.StringVar()
		self.status_var.trace("w", self.timer)# timer() is called when status_var gets written (-->argument "w").
		self.status = tk.Label(self, textvariable=self.status_var, bd=1, relief="sunken", anchor="w", bg="white")
		self.status.pack(side="bottom", fill="x")
		
		# Enter Button and Entry
		self.enter_butt = tk.Button(self, text="Enter")
		self.enter_butt.bind('<Button-1>', self.enter)
		self.enter_butt.pack(side="right",pady=15, padx=15)
		
		self.entry_var = tk.StringVar()
		self.entry = tk.Entry(self, textvariable=self.entry_var)
		self.entry.pack(side="right",pady=15)#, ipady=3)
		self.entry.bind('<Return>', self.enter)	
		self.entry.focus()
		
		# Load Frames
		self.frames = {}
		for F in (EntryGUI, MainGUI):# additional frames go here.
			frame = F(master, self)
			self.frames[F] = frame
			frame.grid(row=0, column=0, sticky="nsew")# the frames are put on each other and the active one is raised over.
			
		# Riddle Initialization
		self.active_riddle = Bete()# set first riddle for init.
		self.entrygui_status = 'Type in a keyword and/or press "Enter".'
		self.set_status(self.entrygui_status)
		self.show_frame(EntryGUI)
		self.active_frame = self.frames[EntryGUI]
	
	def clear_status_var(self):
		"""sets the status message to an empty string."""	
		self.status_var.set("")
	
	def cancel(self):
		"""cancels the timer if there is already one active."""
		if self._job is not None:# if within set time the timer is called again, "self._job" is not None.
			self.after_cancel(self._job)
			self._job = None
	
	def timer(self, *args):
		"""timer for calling 'clear_status_var'."""
		status_phrase = self.status_var.get()
		if status_phrase == "":# if status was cleared and set to "empty", nothing happens.
			return
		if status_phrase == self.entrygui_status:# entrygui_status set for the entry page shall not be cleared until it gets overwritten.
			return
		self.cancel()# cancel() stops the execution of a "pending" after() function, if there is one.
		self._job = self.after(7000, self.clear_status_var)# status displayed 7000 milliseconds before clear_status_var() gets called. the function after()(or rather "self._job") returns "None" after set time.
		
	def set_status(self, status):
		"""sets the status message, takes the status string as argument."""
		self.status_var.set(status)
		
	def get_entry(self):
		"""returns the entry string."""
		return self.entry_var.get()
	
	def enter(self, event):
		"""handles the entry string. uses Guard to examine the input."""
		entry_string = self.get_entry()
		
		if not entry_string.isspace():# "isspace()" returns true if the string only contains whitespace characters or is empty, otherwise returns false.
			
			guard = Guard(entry_string, self.active_riddle, self.active_frame)
			if guard.check_key(): 
				
				self.set_active_riddle(guard.next_riddle())
				
				if self.active_frame == self.frames[EntryGUI]:
					self.active_frame = self.frames[MainGUI]
					self.show_frame(MainGUI)# MainGUI frame is raised
					self.configure(bg="dim grey")
				
				self.active_frame.update_content()
				self.active_frame.hint_label.config(fg="red4")
				self.active_frame.hints.grid_remove()
				self.active_frame.hints_visible = False
				
				self.entry_var.set("")

	def show_frame(self, frame_name):
		"""raises the given frame."""
		frame = self.frames[frame_name]
		frame.tkraise()
		
	def set_active_riddle(self,next_riddle):
		"""sets the given riddle as the active one."""	
		self.active_riddle = next_riddle
	
	def get_active_riddle(self):
		"""returns the active riddle."""
		return self.active_riddle	
	
	
class EntryGUI(tk.Frame):
	"""EntryGUI Frame"""
	
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		
		self.configure(bg="red4")
		controller.configure(bg="red4")
		
		# Intro Label
		entry_label = tk.Label(self, text="the RIDDLER", bg="red4", font=("Courier", 54, "bold"))
		entry_label.pack(expand=True)#in this special case "expand" centers the (only and small enough) widget on the frame, so this does the job.
		
		self.count = 0
		def display_phrase(event):
			"""shows some phrases in the EntryGUI when the label is clicked."""	
			def throw_phrase(phrase):
				phrase_label = tk.Label(self, text=phrase, fg="dim grey", bg="red4", font=("Courier", 10))
				phrase_label.pack()
			
			phrase1="""...because sth like "mystery crate" would sound lame, that's why.\n now go on :-)"""
			phrase2="could you please stop that."
			phrase3="what's wrong?"
			phrase4=""
			phrase5="WOW.\n"
			
			if self.count == 0:
				throw_phrase(phrase1)
			elif self.count == 3:
				throw_phrase(phrase2)
			elif self.count ==5:
				throw_phrase(phrase3)
			elif self.count < 13:
				throw_phrase(phrase4)
			elif self.count == 15:
				throw_phrase(phrase5)
			
			self.count = self.count + 1
		
		entry_label.bind("<Button-1>", display_phrase)
		entry_label.bind("<Button-3>", display_phrase)
		
	
	def update_content(self):
		"""dummy. empty function."""
		pass# dummy
	
	def get_chosen_path(self):
		"""dummy. empty function."""
		pass# dummy	

		
class MainGUI(tk.Frame):
	"""MainGUI Frame"""
	
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		
		self.configure(bg="dim grey")
		
		# Image		
		self.image_label = tk.Label(self, bg="red4")
		self.image_label.grid(row=0, pady=15, padx=15, sticky="nw")
		
		# Download Button
		self.download_butt = tk.Button(self, text="Download", command=self.save_file)
		self.download_butt.grid(row=0, column=1, sticky="se", pady=15, padx=15)

		# Description
		self.description_var = tk.StringVar()
		self.description = tk.Label(self, textvariable=self.description_var, bg="dim grey", justify="left")
		self.description.config(font=(24))
		self.description.grid(row=1, columnspan=4, padx=15, sticky="w")		
		
		# Hints
		self.hints_visible = False# assignment before reference
		self.hint_label = tk.Label(self, text="\n\nHints:\n", bg="dim grey", fg="red4")
		self.hint_label.config(font=(22))
		self.hint_label.grid(row=2,padx=15, sticky="w")
		self.hint_label.bind("<Button-1>", self.toggle_hints)
			
		self.hint_var = tk.StringVar()
		self.hints = tk.Label(self, textvariable=self.hint_var, bg="dim grey", justify="left")
		self.hints.grid(row=3, columnspan=2, padx=18, sticky="w")
		self.hints.grid_remove()		
	
	def toggle_hints(self, event):
		"""shows/hides the hints."""
		if self.hints_visible:
			self.hints.grid_remove()
			self.hint_label.config(fg="red4")
			self.hints_visible = False
		else:	
			self.hints.grid(row=3, columnspan=2, sticky="w")
			self.hint_label.config(fg="black")
			self.hints_visible = True

	def save_file(self):
		"""saves the active riddle's file(if found) to the chosen directory."""
		active_riddle = app.get_active_riddle()
		
		# call of CustomDialog for the riddle "Scellé"
		if isinstance(active_riddle, Scelle):
			number = CustomDialog(self, 
						"Hold on!!\n"
					+	"Amount of 'HTWG' strings in the website's source code:"
				).show()
			amount = active_riddle.get_amount()	
			if amount == False:
				app.set_status("Couldn't connect to the homepage. I need this.")	
				return
			if number == amount:
				app.set_status('Well done! ...Password for the ZIP file is website\'s "favicon".')
			else:
				app.set_status("Sorry, this doesn't seem to be the right amount...")	
				return
			
		self.chosen_path = filedialog.askdirectory()
		if self.chosen_path:
			copy2(active_riddle.get_file_path(), self.chosen_path)

	def set_hint_var(self):
		"""sets/refreshes the hint text."""
		hint = app.get_active_riddle().get_hint()	
		self.hint_var.set(hint)
	
	def set_description_var(self):
		"""sets/refreshes the description text."""
		description = app.get_active_riddle().get_description()
		self.description_var.set(description)
			
	def load_photo(self):
		"""opens and converts the active riddle's image, then returns it"""
		photo = Image.open(app.get_active_riddle().get_photo_path())
		photo.thumbnail((450, 450), Image.BICUBIC)# "thumbnail()" keeps the aspect ratio. if the images are smaller, they may appear smaller, but they never will be bigger than (450,450). BICUBIC is the render method.
		img = ImageTk.PhotoImage(photo)
		return img
		
	def set_image(self):
		"""sets the image from load_photo"""
		img = self.load_photo()
		self.image_label.configure(image=img)
		self.image_label.image = img # keeps a reference to the tkinter object by attaching it to a widget attribute. Otherwise it will be "destroyed"(blanked) by pythons garbage collector.
		
	def update_content(self):
		"""updates the data to the active riddle's"""
		self.set_hint_var()
		self.set_description_var()
		self.set_image()
		
	def get_chosen_path(self):
		return self.chosen_path
	
	
class Guard(object):
	"""Password Examiner"""
	
	wrong_key_answers = ["Wrong password.", "Wrong.", "No, unfortunately.", 
		"Wrong key.", "Nope.", "No.", "Invalid.", "This is wrong.", "Sorry.", 
		"I am so happy right now.", "You're doin' great! :-)"] 
	
	wrong_key_on_entry_screen_answer = 'No matching keyword. Clear the entry and press "Enter" to start with the first riddle.'
	
	def __init__(self, entry_string, active_riddle, active_frame):
		self.key = entry_string
		self.active_riddle = active_riddle
		self.active_frame = active_frame
	
		self.riddles = {
			'': Bete(),
			Bete().get_solution(): Raccourci(),
			#Raccourci(active_frame).get_solution(): Interieur(),
			Raccourci(active_frame).get_solution(): Apesanteur(),
			#Interieur().get_solution(): Apesanteur(),
			Apesanteur().get_solution(): Habitudes(),
			Habitudes().get_solution(): Salade(),
			Salade().get_solution(): Rarete(),
			Rarete().get_solution(): Motif(),
			Motif().get_solution(): Inverse(),
			Inverse().get_solution(): Scelle(),
			Scelle().get_solution(): Jeux(),
			Jeux().get_solution(): Secrets(),
			Secrets().get_solution(): Devoilement(),
			Devoilement().get_solution(): Vide(),
			Vide().get_solution(): Recherche(),
			Recherche().get_solution(): Progres(),
			Progres().get_solution(): Enroulement()	
		}# this dict connects the key words of the previous riddles with the upcoming ones.	
			
	def check_key(self):	
		"""accepts/denies the key."""
		# workaround for the riddle "Raccourci".
		if isinstance(self.active_riddle, Raccourci):# removes the characters '",\,/' and space from the entry string if the active_riddle is "Raccourci". This is mangy.
			to_remove = '"/\\ '
			for chars in to_remove:
				self.key = self.key.replace(chars, "")
			self.key = self.key.replace("Set-Location", "cd")# The "Set-Location" command is an alias for "cd" in the shell and would therefore be part of a right answer too.	
		
		search_result = self.riddles.get(self.key)
		if search_result:
			app.set_status("Riddle " + '"' + search_result.__class__.__name__ + '"'# shows the class name of active riddle
				+ ' - '
				+ 'Topic: '
				+ search_result.get_topic()# shows the topic
			)
			return True
		else:
			self.set_status_phrase()
			return False
	
	def next_riddle(self):
		"""returns the next riddle after key was accepted."""
		return self.riddles.get(self.key)
		
	def set_status_phrase(self):
		"""sets the corresponding status phrase to the wrong entry if there is one."""
		search_result = self.active_riddle.get_status_phrases().get(self.key)
		
		if search_result:
			app.set_status(search_result)	
		else:
			if isinstance(self.active_frame, EntryGUI):
				app.set_status(self.wrong_key_on_entry_screen_answer)
				return
				
			answer = self.wrong_key_answers[randint(0, len(self.wrong_key_answers)-1)]
			app.set_status(answer)	

					
class CustomDialog(tk.Toplevel):
	"""Dialog with Label, Entry, and OK Button"""   
	
	def __init__(self, parent, prompt):
		tk.Toplevel.__init__(self, parent)
		
		# Prompt Label
		self.label = tk.Label(self, text=prompt)
		self.label.pack(side="top", fill="x",pady=5, padx=5)
		
		# Entry
		self.dialog_var = tk.StringVar()
		self.entry = tk.Entry(self, textvariable=self.dialog_var, bd=3)
		self.entry.pack(side="top", fill="x",pady=5, padx=5)
		self.entry.bind("<Return>", self.on_ok)
		
		# OK Button
		self.ok_button = tk.Button(self, text="OK", command=self.on_ok)
		self.ok_button.pack(pady=5)
		
		self.geometry("+%d+%d" % (parent.winfo_rootx()+10, parent.winfo_rooty()+15))
		self.resizable(width=False, height=False)
		
		self.grab_set()# makes the risen dialog modal.
		
	def on_ok(self, event=None):
		self.destroy()

	def show(self):
		self.wm_deiconify()
		self.entry.focus_force()
		self.wait_window()
		return self.dialog_var.get()

		
app = RiddlerGUI()
app.mainloop()