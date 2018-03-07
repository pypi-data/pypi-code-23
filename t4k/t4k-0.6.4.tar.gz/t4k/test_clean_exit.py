#!/usr/bin/env python
'''
This manually tests whether PersistentOrderedDict makes a clean exit when 
a script is terminated while it is trying to sync to file.

To test it, run this file with the arugment 'pod', and hit Ctl-C when 
prompted to.  The script will exit with an Exception (but not a 
KeyboardInterrupt).  Then, try running the script again.  If the exit was 
graceful, execution should appear to be the same.  If the exit was not 
graceful, the script will have an exception, with a complaint from 
PersistentOrdederedDict that the file was corrupted

To do an equivalent test for ProgressTracker, follow the same steps as 
above, but use the argument 'tracker' when running this script.

The exit should always be graceful.  If the line within __init__() for
PersistentOrderedDict starting with "atexit" is commented out, this
manual test will no longer pass.
'''


import sys
import t4k


def run_tracker_test():
	tracker = t4k.ProgressTracker('test-dict')

	print 'initializing...'

	tracker.hold()
	for i in range(5000):
		tracker[str(i)] = {'test':False}
	tracker.unhold()

	print 'Done.  Hit Ctl+C !'
	try:
		for i in range(4000):
			tracker[str(i)] = {'test':True}
	except KeyboardInterrupt:
		print 'Good. Now an error should get thrown...'
	else:
		print 'You weren\'t fast enough!'

	tracker = t4k.ProgressTracker('test-dict')

	print 'Hmm... maybe you took to long to hit Ctr+C...'


def run_pod_test():
	pod = t4k.PersistentOrderedDict('test-dict')

	print 'initializing...'

	pod.hold()
	for i in range(5000):
		pod[str(i)] = {'test':False}
	pod.unhold()

	print 'Done.  Hit Ctl+C !'
	try:
		for i in range(4000):
			pod[str(i)] = {'test':True}
	except KeyboardInterrupt:
		print 'Good. Now an error should get thrown...'
	else:
		print 'You weren\'t fast enough!'

	pod = t4k.PersistentOrderedDict('test-dict')

	print 'Hmm... maybe you took to long to hit Ctr+C...'


if __name__ == '__main__':
	usage = (
		'\nusage:\n\t./test_clean_exit.py pod'
		'\n\t./test_clean_exit.py tracker\n'
	)

	try:
		if sys.argv[1] == 'pod':
			run_pod_test()
		elif sys.argv[1] == 'tracker':
			run_tracker_test()
		else:
			print usage

	except IndexError:
		print usage
