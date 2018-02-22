"""
File overlays for providing files to web applications.
"""
import os

class FileOverlay(object):
	"""
	This is the main file overlay providing methods on files 
	that are useful when operating over a remote connection.

	``path``
		relative path of the file
	``root``
		absolute path of the "root" directory for files,
		``os.path.join(root, path)`` must be the absolute path
		of the file
	``modes`` 
		string or list of characters: 

		- ``"r"`` readable
		- ``"w"`` writable
		- ``"c"`` file can be created
		- ``"p"`` also parent directories can be created.

	``nickname``
		the name of the file that the client knows.
	"""
	def __init__(self, path, root, modes, nickname, maxsize = float("inf"), cpy_chunk_size = 255):
		self._path = path
		self._root = root
		self._modes = modes
		self._abspath = os.path.join(root, path)
		self._nickname = nickname
		self._maxsize = maxsize
		self._cpy_chunk_size = cpy_chunk_size
		try:
			self._size = os.stat(self._abspath).st_size
		except:
			self._size = 0

	def get_file_part(self, offset, chunk_size):
		"""
		Return a ``FilePart`` of this file.
		"""
		if(not "r" in self._modes):
			raise IOError("file is not readable")
		if(not os.path.exists(self._abspath)):
			raise IOError("file does not exist")

		fout = open(self._abspath, "rb")
		return FilePart(fout, offset, chunk_size)

	def write_file_part(self, offset, chunk):
		"""
		Write a part of a file. If the file is not at least ``offset``
		bytes long, raise ``IndexError``. This is a protection against
		people that think it would be funny to fill the disk up with zeros.
		"""

		if(not "w" in self._modes):
			raise IOError("file is not writable")

		chunk_size = len(chunk)
		tail = offset - self._size + chunk_size
		if(tail + self._size > self._maxsize):
			raise IOError("maximum file size exceeded")

		if(not os.path.exists(self._abspath)):
			if(not "c" in self._modes):
				raise IOError("file does not exist")
			self.create_file()

		if(offset > self._size + 1):
			raise IndexError("file size exceeded")

		with open(self._abspath, "r+b") as fin:
			fin.seek(offset)
			fin.write(chunk)

		# FIXME:
		# This is just for testing. In a production
		# environment the FileOverlay should be deleted once
		# an operation has been issued.
		# This is just natural.
		self._size = os.stat(self._abspath).st_size

	def copy_file_part(self, offset, file_part):
		"""
		Copy the ``file_part`` to ``offset``.

		This will read ``cpy_chunk_size`` chunks and write them at
		``offset``.

		If the maxsize is exceeded it will stop after writing enough
		chunks to not yet exceed the size.
		"""

		chunk = file_part.read(self._cpy_chunk_size)
		c_offset = offset
		while(chunk):
			self.write_file_part(c_offset, chunk)
			# FIXME:
			# Check whether it would be o.k.
			# to just add ``self._cpy_chunk_size`` instead
			# of calculating the length of the chunk.
			c_offset += len(chunk)
			chunk = file_part.read(self._cpy_chunk_size)


	def truncate(self, size = None):
		"""
		Truncate the file to ``size``. 
		"""
		if(not "w" in self._modes):
			raise IOError("file is not writable")

		if(not os.path.exists(self._abspath)):
			if(not "c" in self._modes):
				raise IOError("file does not exist")
			self.create_file()
			return

		with open(self._abspath, "r+b") as f:
			f.truncate(size)



	def create_file(self):
		"""
		Create the file or raise IOError.
		"""
		if(not "c" in self._modes):
			raise IOError("file ist not creatable")
		if(os.path.exists(self._abspath)):
			raise IOError("file does exist")

		if(not os.path.exists(os.path.dirname(self._abspath))):
			if(not "p" in self._modes):
				raise IOError("parent path cannot be created")
			os.makedirs(os.path.dirname(self._abspath))
		open(self._abspath, "wb").close()

	def remove_file(self):
		"""
		Remove this file.
		"""

		if(not "w" in self._modes):
			raise IOError("file is not writable")

		os.remove(self._abspath)




class FilePart(object):
	"""
	This represents a readable file part.
	"""
	def __init__(self, file_, offset, chunk_size):
		self._file = file_
		self._offset = offset
		self._chunk_size = chunk_size
		self._cursor = offset
		self._file.seek(offset)

	def read(self, cnt = None):
		"""
		``read`` from the file. Do not read further than ``offset + chunk_size``.
		"""
		left = self._offset + self._chunk_size - self._cursor

		if(cnt == None):
			cnt = left

		if(cnt > left):
			cnt = left

		self._cursor += cnt
		return self._file.read(cnt)
	def close(self):
		"""
		Close the underlaying file.
		"""
		return self._file.close()
	def seekable(self):
		return False
	def writable(self):
		return False
	def readable(self):
		return True
