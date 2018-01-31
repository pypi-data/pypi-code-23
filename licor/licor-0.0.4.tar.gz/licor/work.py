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


from .filediscovery import discover_all, discover_this_path
import os

def work_one(path, callbacks):
	"""
	Run all callbacks for the given path.

	All the callbacks should return any value that
	evals to False. If one callback returns a value
	that evals to True the rest of the callbacks is skipped.
	"""

	for callback in callbacks:
		if(callback(path)):
			break

def work_all(path, file_ending, callbacks, ignore_paths = [], ignore_files = []):
	"""
	Walk over all matching files  matched by ``discover_all``.
	"""
	for this_path in discover_all(path, file_ending, ignore_paths):
		if(this_path in ignore_files):
			continue
		work_one(this_path, callbacks)
	
def work_this_path(path, file_ending, callbacks, ignore_files = []):
	"""
	Walk over all matching files matched by ``discover_this_path``.
	"""

	for this_path in discover_this_path(path, file_ending):
		if(this_path in ignore_files):
			continue
		work_one(this_path, callbacks)

