#Coded by EV_EV
from inspect import currentframe,getframeinfo
def r(ex):
	cf = currentframe()
	#Get the line
	line=cf.f_back.f_lineno
	print('Traceback:\n'+ex+'\nin line '+str(line))
	wait=input('Press Enter to continue excecution.')