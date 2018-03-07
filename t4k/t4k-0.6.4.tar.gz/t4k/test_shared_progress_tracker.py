#!/usr/bin/env python

import shutil
import multiprocessing
from multiprocessing.managers import BaseManager
import time
import random
import t4k

def run_test1():
	tracker = t4k.SharedProgressTracker('test_dict')

	p1 = multiprocessing.Process(
			target=test_concurrent_write, args=(tracker,'A'))
	p2 = multiprocessing.Process(
			target=test_concurrent_write, args=(tracker,'B'))

	p1.start()
	p2.start()

	p1.join()
	p2.join()

	print tracker['yo'], '(should be 20000.)'
	tracker.close()


def run_test2():
	tracker = t4k.SharedProgressTracker('test_dict')

	p1 = multiprocessing.Process(target=test_hold, args=(tracker,'A'))
	p2 = multiprocessing.Process(target=test_hold, args=(tracker,'B'))

	start_time = time.time()

	p1.start()
	p2.start()

	p1.join()
	p2.join()

	print [int(tracker['A:'+str(i)] - start_time) for i in range(10)]
	print [int(tracker['B:'+str(i)] - start_time) for i in range(10)]
	print (
		'(numbers in second list should all be greater than or equal'
		' to those in first list.)'
	)

	tracker.close()


def test_hold(tracker, name):
	tracker.hold()
	for i in range(10):
		print '+'
		time.sleep(random.random())
		tracker['%s:%d' % (name, i)] = time.time()
	tracker.unhold()


def test_concurrent_write(tracker, name):
	for i in range(10000):
		if i % 1000 == 0:
			print '.'
		tracker.hold()
		if 'yo' in tracker:
			tracker['yo'] += 1
		else:
			tracker['yo'] = 1
		tracker.unhold()





# Tried doing this using a manager

POD_PUBLIC_METHODS = [
	'hold',
	'unhold',
	'keys',
	'values',
	'read',
	'mark_dirty',
	'sync',
	'escape_key',
	'__iter__',
	'next',
	'__contains__',
	'__len__',
	'__getitem__',
	'ensure_unicode',
	'update',
	'__setitem__',
	'check_or_add',
	'set_item',
	'set',
	'check',
	'add',
	'increment_tries',
	'reset_tries',
	'mark_done',
	'mark_not_done',
]


def test_manager():

	class MyManager(BaseManager):
		pass

	MyManager.register(
		'ProgressTracker', t4k.ProgressTracker, exposed=POD_PUBLIC_METHODS
	)
	manager = MyManager()
	manager.start()

	tracker = manager.ProgressTracker('test_dict')

	p1 = multiprocessing.Process(
		target=test_concurrent_write, args=(tracker,'A'))
	p2 = multiprocessing.Process(
		target=test_concurrent_write, args=(tracker,'B'))

	p1.start()
	p2.start()

	p1.join()
	p2.join()

	print tracker['yo']


if __name__=='__main__':
	# Remove pre-existing left-over test files from previous test
	t4k.ensure_removed('test_dict')

	# Run tests
	#test_manager()
	#run_test2()
	run_test1()
