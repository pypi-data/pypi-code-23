import pytest
from webdb.files.file import FileOverlay
import os

def test_fileoverlay(tmpdir):
	root = tmpdir

	# File that cannot be created because the "c" flag is 
	# not set.
	f = FileOverlay("doesnotexist", root, "rw", "doesnotexist")
	with pytest.raises(IOError):
		f.write_file_part(0, b"foo")

	with pytest.raises(IOError):
		f.get_file_part(0, 0).read()

	with pytest.raises(IOError):
		f.truncate()
	
	with pytest.raises(IOError):
		f.create_file()
	
	# File that can created
	f = FileOverlay("doesnotyetexist", root, "rwc", "doesnotyetexist")
	with pytest.raises(IOError):
		f.get_file_part(0, 0).read()

	f.write_file_part(0, b"foo")

	assert f.get_file_part(0, 4).read() == b"foo"
	
	with pytest.raises(IndexError):
		f.write_file_part(10, b"bar")
	assert f.get_file_part(0, 4).read() == b"foo"

	f.write_file_part(3, b"bar")
	assert f.get_file_part(0, 10).read() == b"foobar"
	assert f.get_file_part(1, 3).read() == b"oob"

	f.truncate(3)
	assert f.get_file_part(0, 10).read() == b"foo"

	# File that cannot be created because the parent
	# does not exist.
	f = FileOverlay("cannot/exist", root, "rwc", "cannot/exist")
	with pytest.raises(IOError):
		f.write_file_part(0, b"foo")

	with pytest.raises(IOError):
		f.get_file_part(0, 0).read()

	with pytest.raises(IOError):
		f.truncate()
	
	with pytest.raises(IOError):
		f.create_file()

	# We created that earlier
	f = FileOverlay("doesnotyetexist", root, "rw", "doesnotyetexist")
	f.write_file_part(3, b"bar")
	assert f.get_file_part(0, 10).read() == b"foobar"


	# check whether quotas work
	f = FileOverlay("doesnotyetexist", root, "rw", "doesnotyetexist", 10)
	with pytest.raises(IOError):
		f.write_file_part(3, b"foo"*10)

	# check whether permissions work
	f = FileOverlay("doesnotyetexist", root, "r", "doesnotyetexist")
	with pytest.raises(IOError):
		f.write_file_part(3, b"foo"*10)
	assert f.get_file_part(0, 10).read() == b"foobar"

	f = FileOverlay("doesnotyetexist", root, "", "doesnotyetexist")
	with pytest.raises(IOError):
		f.write_file_part(3, b"foo"*10)
	with pytest.raises(IOError):
		assert f.get_file_part(0, 10).read() == b"foobar"
	


	# File that can be created, because the "p" flag is set.
	f = FileOverlay("can/create", root, "rwpc", "can/create")
	f.write_file_part(0, b"foo")
	assert f.get_file_part(0, 10).read() == b"foo"

	# Check whether deleting works
	f = FileOverlay("doesnotyetexist", root, "rw", "doesnotyetexist")
	assert f.get_file_part(0, 10).read() == b"foobar"
	f.remove_file()
	with pytest.raises(IOError):
		 assert f.get_file_part(0, 10).read() == b"foobar"


