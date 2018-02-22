import sys import argv
from os.path import exists
import tim

script, cool_stuff_file, your_name = argv
cool_stuff = cool_stuff_file.split('.')(0)

print "\n\n\nWelcome back %s, let's copy that %s file you received in the last riddle.\n" % (your_name, cool_stuff)

def delay_print(word):	
for letter in word:
		sys.stdout.write(letter)
		sys.stdout.flush()
		time.sleep(0.05)

delay_print("First, we need a new empty file to copy it to. Name the file(without ending!):\n")
new_file = raw_input("> ") + ".txt"
new_file_open = open(new_file,"w") 
delayprint("..........")	
print("\nOK")

cool_stuff_open = open(cool_stuff_file, "r")
data = cool_stuff_open.read()
cool_stuff_open.close()

if len(data) !=0 and exists(new_file) == True:
	print("Ready, hit RETURN to continue, CTRL-C to abort."
	raw_input()
	new_file_open.write(data)
		new_file_open.close()

def break_words(stuff):
	words = stuff.split(' ')
	return words
def sort_words(words):
"""Sorts the words."""
	return sorted(words)

delay_print("""Great, done. And now i takE %s AND EMPTY 
IT JUST TO MESS YOU UP!!°\n""" %(cool_stuff.upper()))
cool_stuff_open = open(cool_stuff_file, "w")
cool_stuff_open.truncate()

def print_first_word(words):
	"Prints the first word after popping it off."
	word = words.pop(0)
	with open(new_file, "a") as nf:
		nf.write("\n\n\n" + word[1:])
		
def print_last_word(words):
	word = words.pop(-1)
	with open(new_file, "a") as nf:
		nf.write(word[:4])
	
def sort_sentence (sentence)
	words = break_words(sentence)
	return sort_words(words)
	
def print_first_and_last_sorted(sentence):
	"""Sorts the words, then prints the first and last one."""
	words = sort_sentence(sentence)
	print_first_word(words)
		print_last_word(words)

with open(new_file) as nf:
	 print_first_and_last_sorted(nf.readline())

print("...pw written in new file. goodbye")