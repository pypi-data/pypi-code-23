import multiprocessing
from multiprocessing.managers import BaseManager


class MyManager(BaseManager):
	pass

class MyObject(object):
	def __init__(self):
		self.val = 0

	def inc(self):
		self.val += 1

	def get(self):
		return self.val


MyManager.register('MyObject', MyObject, exposed=['get', 'inc'])


def test_manager():
	manager = MyManager()
	manager.start()
	my_object = manager.MyObject()

	p1 = multiprocessing.Process(target=do_increment, args=(my_object,'A'))
	p2 = multiprocessing.Process(target=do_increment, args=(my_object,'B'))

	p1.start()
	p2.start()

	p1.join()
	p2.join()

	print my_object.get()


def do_increment(obj, name):
	for i in range(10000):

		if i % 1000 == 0:
			print name

		obj.inc()


if __name__=='__main__':
	test_manager()
