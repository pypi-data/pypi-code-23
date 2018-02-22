import pytest
from webdb.files.dispatcher import SQLFileDispatcher
import os, sqlite3, logging

@pytest.fixture
def default_sqldispatcher(tmpdir_factory):
	#
	# Set up everything
	
	root = tmpdir_factory.mktemp('data')

	db = sqlite3.connect(os.path.join(root, "dispatch.db"))

	setup = ["CREATE TABLE files(" \
			"path text UNIQUE, " \
			"id integer PRIMARY KEY AUTOINCREMENT, " \
			"max_size integer)",
		"CREATE TABLE access(file_id integer," \
			"username text," \
			"modes text)",
		"CREATE TABLE nicknames(name text PRIMARY KEY," \
			"file_id integer)",
		"CREATE INDEX access_index ON access(file_id)",
		"CREATE TABLE root(root text UNIQUE)"]
		

	cursor = db.cursor()

	for cmd in setup:
		cursor.execute(cmd)
		db.commit()

	cursor.execute("INSERT INTO root VALUES(?)", [str(root)])
	db.commit()
	cursor.executemany("INSERT INTO files(path, max_size) VALUES(?, ?)",
			[("file1.tx", -1), ("file2.tx", 10), ("file3.tx", 100)])
	db.commit()

	cursor.executemany("INSERT INTO nicknames(name, file_id) VALUES(?, ?)",
			[("file1.tx", 1), ("file2.tx", 2), ("file3.tx", 3),
			("alias1", 1), ("alias2", 2), ("alias3", 3), ("file4.tx", 3)])
	db.commit()

	cursor.executemany("INSERT INTO access(username, modes, file_id) VALUES(?, ?, ?)",
			[("user1", "rw", 1), ("user2", "rw", 2), ("user3", "rw", 3),
			 ("user2", "r", 1), ("user2", "rw", 3)])
	db.commit()

	for i in ["file1.tx", "file2.tx", "file3.tx"]:
		open(os.path.join(root, i), "w").close()

	# Setup is done
		
	dispatcher = SQLFileDispatcher(db)

	return dispatcher


def test_aliasing(default_sqldispatcher, caplog):
	caplog.set_level(logging.INFO)
	dispatcher = default_sqldispatcher

	f = dispatcher.dispatch_file("alias1", "user1")
	f.write_file_part(0, b"hello, world")
	assert f.get_file_part(0, 20).read() == b"hello, world"

	f = dispatcher.dispatch_file("alias1", "user2")
	assert f.get_file_part(0, 20).read() == b"hello, world"

	f = dispatcher.dispatch_file("file1.tx", "user1")
	assert f.get_file_part(0, 20).read() == b"hello, world"



def test_access(default_sqldispatcher, caplog):
	caplog.set_level(logging.INFO)
	dispatcher = default_sqldispatcher

	f = dispatcher.dispatch_file("alias1", "user2")
	assert f.get_file_part(0, 20).read() == b""
	with pytest.raises(IOError):
		f.write_file_part(0, b"hello, world")
	assert f.get_file_part(0, 20).read() == b""
	
	f = dispatcher.dispatch_file("alias1", "user1")
	f.write_file_part(0, b"hello, world")
	assert f.get_file_part(0, 20).read() == b"hello, world"



