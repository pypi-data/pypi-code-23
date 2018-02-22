import pytest
from webdb.files.dispatcher import UserFileDispatcher, QuotaUserFileDispatcher
import os


def test_userdispatcher(tmpdir):
	root = tmpdir

	dispatcher = UserFileDispatcher(root)

	f1 = dispatcher.dispatch_file("test.tx", "user1")
	f2 = dispatcher.dispatch_file("test.tx", "user2")
	f3 = dispatcher.dispatch_file("test/test.bar", "user1")

	f1.write_file_part(0, b"test")
	assert f1.get_file_part(0, 10).read() == b"test"

	with pytest.raises(IOError):
		f2.get_file_part(0, 10)
	
	f2.write_file_part(0, b"yet another test")
	assert f2.get_file_part(0, 30).read() == b"yet another test"
	assert f1.get_file_part(0, 10).read() == b"test"

	f3.write_file_part(0, b"third test")
	assert f3.get_file_part(0, 10).read() == b"third test"


def test_quotauserdispatcher(tmpdir):
	root = tmpdir

	dispatcher = QuotaUserFileDispatcher(root, 100)

	f1 = dispatcher.dispatch_file("test.tx", "user1")
	f2 = dispatcher.dispatch_file("test.tx", "user2")
	f3 = dispatcher.dispatch_file("test/test.bar", "user1")

	f1.write_file_part(0, b"test")
	assert f1.get_file_part(0, 10).read() == b"test"

	with pytest.raises(IOError):
		f2.get_file_part(0, 10)
	
	f2.write_file_part(0, b"yet another test")
	assert f2.get_file_part(0, 30).read() == b"yet another test"
	assert f1.get_file_part(0, 10).read() == b"test"

	f3.write_file_part(0, b"third test")
	assert f3.get_file_part(0, 10).read() == b"third test"


	dispatcher = QuotaUserFileDispatcher(root, 10)
	f1 = dispatcher.dispatch_file("test.tx", "user1")

	with pytest.raises(IOError):
		f1.write_file_part(0, b"test"*10)

	f2 = dispatcher.dispatch_file("test2.tx", "user1")
	f2.write_file_part(0, b"test")
	with pytest.raises(IOError):
		f1.write_file_part(0, b"this exceeds")

	f3 = dispatcher.dispatch_file("test3.tx", "user2")
	f3.write_file_part(0, b"this fits")


