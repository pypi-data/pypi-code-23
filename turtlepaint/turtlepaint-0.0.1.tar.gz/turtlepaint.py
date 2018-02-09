#!/usr/bin/python3

########################
#      TurtlePaint     #
# (very original name) #
# Made By Trevor Brown #
#       02/08/18       #
########################

# pretty standard imports
import turtle, os, sys

# cross-platform screen clearing
def clear():return (" " if os.system("cls" if os.name == "nt" else "clear") == 0 else " ")
clear()

# complicated try-except sieve for getting libraries that can save your creations
cansave = False
try:
	from PIL import ImageGrab
except:
	try:
		import PIL
	except:
		print("Try 'pip install PIL', 'pip install pillow', or 'pip install pyscreenshot'.")
	else:
		try:
			import pyscreenshot as ImageGrab
		except:
			print("Try 'pip install pyscreenshot'")
		else:
			cansave = True
else:
	cansave = True

# a simple library I wrote to filter out bad color names
try:
	from tkcolorlist import colors
except:
	print("You can get tkcolorlist through pip!")
	colors = ["red","orange","yellow","green","blue","purple","white","black","gray","grey","pink","brown","indigo","violet"]
	print("Using a very limited color list instead.")

# defining all of the functions available through the menu
def togglepen(t):(t.penup if t.pen()['pendown'] else t.pendown)()
def togglefill(t):(t.end_fill if t.filling() else t.begin_fill)()
def hideshow(t):(t.hideturtle if t.isvisible() else t.showturtle)()
def moveleft(t):t.left(45)
def moveright(t):t.right(45)
def forward(t):t.forward(15)
def back(t):t.back(15)
def changecolor(t):(lambda n,t:t.color(n if n in colors else ("" if print("Not a valid color name.") == None else "")+t.color()[0]))(input("name a color: "),t)
def quit(t):sys.exit(clear())
def save(t,fn):(lambda x=print(" Saved to \'" + ("unturtled.png" if (fn + " ") == " " else fn)+(".png" if (fn[-4:] != ".png" and (fn + " ") != " ") else '') + "\'."):ImageGrab.grab().crop((t._screen._canvas._root().winfo_rootx()+t._screen._canvas.winfo_x()+10,t._screen._canvas._root().winfo_rooty()+t._screen._canvas.winfo_y()+10,t._screen._canvas._root().winfo_rootx()+t._screen._canvas.winfo_x()+10+t._screen._canvas.winfo_width()-20,t._screen._canvas._root().winfo_rooty()+t._screen._canvas.winfo_y()+10+t._screen._canvas.winfo_height()-20)).save(("unturtled.png" if (fn + " ") == " " else fn)+(".png" if (fn[-4:] != ".png" and (fn + " ") != " ") else "")))()
def sorry(t,fn):print("\n Sorry, you can't do that.")
def size(t):t.pensize(float(input("\n\n New size: ")))
def null(x):return
def background(t):(lambda n,t:t._screen._bgcolor(n if n in colors else ("" if print("Not a valid color name.") == None else "")+t._screen._bgcolor()))(input("name a color: "),t)

# dictionary of single-letter menu options and their corresponding functions
commands = {"t":togglepen, "i":togglefill, "l":moveleft, "r":moveright, "f":forward, "b":back, "c":changecolor, "q":quit, "s":(save if cansave else sorry), "g":hideshow, "z":size, "d":background}

# init turtle
t = turtle.Turtle()

# init warning variable
warnmsg = ""

while True: # will be exited by exit(), so a True loop is fine
	# print main menu
	print()
	print(" ,-------------------------.")
	print(" | ,---------------------. |")
	print(" | |>~~~{TURTLEPAINT}~~~<| |")
	print(" | `---------------------' |")
	print(" |-------------------------|")
	print(" | PEN CONTROL:            |")
	print(" |                         |")
	print(" | [T]      toggle pen (" + ("v" if t.pen()['pendown'] else "^") + ") |") # "v" if down,    "^" if up
	print(" | [I]     toggle fill (" + ("/" if t.filling() else " ") + ") |")        # "/" if filling, " " if not
	print(" | [G]   toggle turtle (" + ("S" if t.isvisible() else "H") + ") |")      # "S" if showing, "H" if hidden
	print(" |-------------------------|")
	print(" | PEN PROPERTIES:         |")
	print(" |                         |")
	print(" | [D]     change bg color |")
	print(" | [C]        change color |")
	print(" | [Z]         change size |")
	print(" |-------------------------|")
	print(" | MOVEMENT:               |")
	print(" |                         |")
	print(" | [L]           turn left |")
	print(" | [R]          turn right |")
	print(" | [F]        move forward |")
	print(" | [B]       move backward |")
	print(" |-------------------------|")
	print(" | UTILITIES:              |")
	print(" |                         |")
	(print if cansave else null)(" | [S]                save |") # won't show if you can't save
	print(" | [Q]                quit |")
	print(" `-------------------------'")

	# get user's choice from menu
	choice = (input(warnmsg+"\n\n > ").lower()+" ")[0] # only get the first letter, in lowercase, and don't give an error if nothing is entered

	# the art of lambdas is confusing to most. but hey, it works!
	warnmsg = (((lambda x=commands[choice](t,input("\n Please move all windows from on top of the turtle display window.\n\n  Save as: ")):clear()) if choice=="s" else (lambda x=commands[choice](t):clear())) if choice in commands.keys() else (lambda x=clear():"Not a valid option."))()
