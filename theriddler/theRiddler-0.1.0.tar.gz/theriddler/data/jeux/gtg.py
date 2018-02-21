#*****Gothon Trash Game*****
import sys
import time
from random import randint

class Scene(object):
	
	def enter(self):
		pass
	
	def read_string(self, string):
		for letter in string:
			sys.stdout.write(letter)
			sys.stdout.flush()
			time.sleep(0.05)
		print("\n")
		
	def wrong_entry(self):
		self.read_string("DOES NOT COMPUTE! \nagain...")
	
class Death(Scene):
	
	answers = [
		"You died. You kinda suck at this.",
		"Your mom would be proud if you were smarter.",
		"Everyone here on the whole ship hates you because you're weak af!!!°",
		"...such a looser.",
		"...Leave the computer. Just do it.",
		"Shame.Shame.."
		]
	
	def enter(self):
		answer = Death.answers[randint(0, len(self.answers)-1)]
		self.read_string(answer)
				
		print("\n...hey stupid, do you want to start over again?")
		print("\nPress (Y/N or sth. else!!)")
		command = input("> ")
		if command == "Y" or command == "y":
			return 'central_corridor'
		else:
			self.read_string(".........FINE!")
			exit(1)
		
class CentralCorridor(Scene):
	
	def enter(self):
		print("\nThe terrible Gothons of Planet Percival #25 have invaded")
		print("your Spaceship and killed your whole crew!!")
		print("Your last mission is to find a way to the Weapon Armory")
		print("to get the neutron destruct bomb, then to put it in the")
		print("bridge, and then to blow the ship up right after getting")
		print("in an escape pod.")
		
		print("\nNow, you find yourself behind a container in the")
		print("central corridor, where you are hiding from a furious")
		print("Gothon you just ran away from. The Gothon has red")
		print('scaly skin, dark grimy teeth, and, assuming his "Christians rock"') 
		print("EdHardy gang banger shirt he wears, he is religious as fork. His body")
		print("is filled with racist hate and bias, and he stands right")
		print("in the middle of the corridor looking for you.")
		
		self.read_string("\nWhat do you do?\n")
		
		print("(1) shoot!")
		print("(2) keep hiding.")
		print("(3) tell a joke.")
		
		print("\nPress a number:")
		action = input("> ")
		
		if action == "1":
			print("\nYou missed the ugly but remarkably strong looking")
			print("Gothon, who has now seen you")
			print("and is both really pissed at you and turned on by your fear.")
			print("He drags you out of your hiding place, disarmes you" )
			print("and rapes you to death. Congratulations!")
			
			return 'death'
		
		elif action == "2":
			print("\nYou keep hiding.")
			print("Nothing happens.. The Gothon scans the whole place and")
			print("finds u in a puddle of your own piss. Then he begins")
			print("to tear your clothes off, just leaving you your")
			print("sweet space helmet, and then suddenly he rapes you to death!!!")
			print("Well done, you little coward!")
			
			return 'death'
			
		elif action == "3":
			print("\nLucky for you they made you learn Gothon jokes in")
			print("the academy, so you tell the only Gothon joke you know:")
			print("\n\tasdlfklkjgl lkjdglkj kjsd fljfei fokjdlks jfls!")
			print("\nThe Gothon hears it, tries not to laugh,")
			print("then bust out laughing and can't move.")
			print("Just in time, you jump out and shoot his head off!")
			print("You're now heading to the Weapon Armory door, feeling")
			print("so strong and straight.")
			
			return 'weapon_armory'

		else:
			self.wrong_entry()
			return 'central_corridor'

class TheBridge(Scene):	
	
	def enter(self):
		print("\nYou burst onto the Bridge with the neutron destruction")
		print("bomb, and all the Gothons around you suddenly")
		print("see the active bomb under your arm.")
		print("They put their hands up now and start to sweat like hell. You can")
		print('see it, as their "Christian rocks" EdHardy shirts from 2004 clearly darken')
		print("a bit under the armpits.")
		print("...Nevertheless. They look kind of great in it! :-)")
		print("One of them is even smiling at you, greets you with a finger gun")
		print("and a little twinkle. Very upsetting, I tell you.")
		
		self.read_string("\nWhat do you do?\n")
		
		print("(1) throw the bomb!")
		print("(2) slowly place the bomb.")
		
		print("\nPress a number:")
		
		action = input("> ")
		
		if action == "1":
			print("\nIn a panic, you throw the bomb at the group of")
			print("Gothons and make a leap for the door. Right as you")
			print("drop it, a Gothon shoots you right in the back,")
			print("and as you lay on the ground, the one with the big smile and")
			print("the finger gun starts with your religious cure, forces")
			print("you to do terrible things. From sight angles you see another Gothon")
			print("frantically try to disarm the bomb. You die knowing")
			print("they will probably blow up when it goes off.")
			print("It hurts but yes, it's OK, you get to believe in god now.")
			print("\n...and everything has to have a reason, so you certainly deserve this!!!!")
			
			return 'death'
		
		if action == "2":
			print("\nYou point the blaster at the bomb under your arm.")
			print("You slowly inch backward to the door that leads to the Escape Pod.")
			print("Then you carefully place the bomb on the floor,")
			print("pointing your blaster at it. You jump back through")
			print("the door, punch the close button and blast the lock,")
			print("so that the upset Gothons can't go after you.")
			print("Now that the bomb is placed, you run to the Escape Pod to")
			print("get off this tin can.")
			
			return 'escape_pod'
		
		else: 
			self.wrong_entry()				
			return 'the_bridge'
			
class WeaponArmory(Scene):
	
	def enter(self):
		print("\nYou do a dive roll into the Weapon Armory, crouch")
		print("forward and scan the room for more christian Gothons.")
		print("It is quiet in here, too quiet, you think...No sounds, except a")
		print("little ticking thing on the other side of the room")
		print("You're jumping up and run to the other side!")
		print("Just behind this massive bulletproof glass, and secured")
		print("with a keypad lock there it is:")
		print("The neutron bomb in its container.") 
		print("You need to type the code to get the bomb out,")
		print("but the problem is, since this whole thing started and")
		print("you shat yourself the first time you saw one of the")
		print("Gothons, you forgot the code!! Oh my... If you get the code wrong")
		print("ten times then the lock closes forever.")
		
		self.read_string("\nThe code is three digits going from 0 to 1:\n")
		
		code = "%d%d%d" % (randint(0,1), randint(0,1), randint(0,1))
		guesses = 0
		guess = input("[keypad]> ")
		
		while guess != code and guesses<10:
			print("BZZZEDDDD!")
			guesses += 1
			guess = input("[keypad]> ")
			
		if guess == code:
			print("\nThe door clicks open and the seal breaks.")
			print("You grab the neutron bomb an run as fast as you can")
			print("to bridge, from where you must place it in the right")
			print("spot to make sure allo them mofos dyin'!")
			
			return 'the_bridge'
		
		else:
			print("\nThe lock buzzes one last time, and then you hear")
			print("a sickening melting sound as the mechanism")
			print("is fused together.")
			print("You decide to sit there, crying, and finally one last")
			print("Gothon comes by to rape you to death, just before")
			print("their Gothon war ship blows up your ship from far")
			print("away and you die. The Gothon that started your treatment stayed to see")
			print("you loose all your hope and dignity, it was a very intimate moment.")
			
			return 'death'
			
class EscapePod(Scene):
	
	def enter(self):
		print("\nYou rush through the ship, desperately trying to make it to")
		print("the escape pod before the whole ship explodes.")
		print("It seems like all the remaining Gothons got together,")
		print("now being busy with doing urgent things like praying, so your run is clear")
		print("of interference. You get to the chamber with the escape pods,")
		print("and you need to pick one to take. Some of them could be damaged...")
		print("\nThere are 3 pods, which one do you take?\n")
		
		good_pod = randint(1,3)
		guess = input("[pod number]> ")

		if guess == good_pod:
			print("\nYou jump into pod %s and hit the eject button." %guess)
			print("The pod escapes out in to the void of space heading to")
			print("the planet below. As it flies to the planet, you look")
			print("back and see your ship implode, then suddenly explode like a")
			print("bright star, which looks so beautiful or so, i can't even")
			print("describe what i'm seeing right now oh my god. And all the Gothons")
			print("are blowing up, too. You loose everything, but you live, and you win")
			print('this game, and the solution to the riddle you just made is of course "EdHardy".')
			self.read_string("........... :-)")
		
			return 'finished'
		
		else:
			print("\nYou jump into pod %s (why ?!?!?!?) and hit the eject button." %guess)
			print("The pod easily slides out, then unfortunately implodes as the")
			print("damaged hull ruptures, crushing your body into jam jelly.")
			print("\nGuess what, it kills you! Wrong pod, i would say. Make a smarter")
			print("choice next time.")
			
			return 'death'