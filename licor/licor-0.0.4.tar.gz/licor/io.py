# Copyright (c) 2017 Daniel Knüttel                                           #
#                                                                             #
# This file is part of licor.                                                 #
#                                                                             #
# licor is free software: you can redistribute it and/or modify               #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# licor is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU Affero General Public License    #
# along with licor.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
#                                                                             #

import os


def check_file_perm(filename):
	"""
	Check wether this process can open this file for R/W.
	"""
	if(not os.path.exists(filename)):
		raise IOError("File not Found: {}".format(filename))

	if(not (os.access(filename, os.R_OK) and os.access(filename, os.W_OK))):
		raise IOError("File not readable/writable: {}".format(filename))


def insert_header(filename, header, chunk_size = 1024, encoding = "UTF-8"):
	"""
	Insert the header ``header`` into the file with the name ``filename``.
	"""
	check_file_perm(filename)

	with open(filename, encoding = encoding) as fin:
		os.unlink(filename)

		with open(filename, "w", encoding = encoding) as fout:
			fout.write(header)

			chunk = fin.read(chunk_size)
			while(chunk):
				fout.write(chunk)
				chunk = fin.read(chunk_size)

	
			

