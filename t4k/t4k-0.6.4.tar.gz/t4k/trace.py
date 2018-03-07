import traceback
import sys


def trace():
	'''
		When called in an except block, returns the stack trace that
		would have been emmitted due to the exception if it were uncaught.
	'''
	return traceback.format_exc(sys.exc_info())


def get_trace():
	'''
		Similar to get_trace, but returns an array of strings, each one
		matching a stack frame.  See trace().
	'''
	# get the stack trace.  
	trc = traceback.format_stack()
	trc =  trc[1:-1]
	trc.append(traceback.format_exc())

	return trc

