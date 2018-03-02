from __future__ import absolute_import

from .module import Zymkey

__all__ = ['Zymkey', 'client']

try:
	client = Zymkey()
except  AssertionError:
	client = None
	pass

def create_new_client():
	try:
		new_client = Zymkey()
	except AssertionError:
		new_client = None
	return new_client

