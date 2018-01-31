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


def pad_line(line, pad_to):
	"""
	Pad line with blanks until the line is ``pad_to``
	long.
	"""

	return line + " " * (pad_to - len(line))

def uncomment_line_based(text, comment_start, 
		fancy = False, 
		after_comment = " ",
		pad_to = 0):
	"""
	Generate an uncommented version of the text that can be inserted into
	a source file.

	If ``fancy`` is False, the code will be just uncommented
	by inserting a ``comment_start`` and a ``after_comment`` at every nonempty line.

	If ``fancy`` is True the block will be padded with blanks
	(either to ``pad_to`` or until the longest line is matched)
	and there will be another ``comment_start`` at the end of
	every line.


	Example::

		uncomment_line_based("This is a text\n\nblock\n", "#")

	Will result in::

		# This is a text
			 
		# block
		
	The trailing newline will be preserved.
	"""

	text = text.split("\n")

	if(not fancy):
		text = [comment_start + after_comment + line if line else line for line in text]
	else:
		max_length = len(max(text, key = lambda x: len(x)))

		if(max_length > pad_to):
			pad_to = max_length

		text = [comment_start + after_comment + 
				pad_line(line, pad_to) + 
				after_comment + comment_start
					for line in text]
	return "\n".join(text)


def uncomment_multiline_line_oriented(text, comment_start, 
		comment_stop, after_comment = " ",
		fancy = False, border = "*", pad_to = 0):
	"""
	Just like ``uncomment_line_based``, but with start and stop
	for comments.

	**Note**: ``border`` must be a length-1 string.
	"""

	text = text.split("\n")
	max_length = len(max(text, key = lambda x: len(x)))

	if(max_length > pad_to):
		pad_to = max_length

	if(not fancy):
		text = [comment_start + after_comment + pad_line(line, pad_to) +
			after_comment + comment_stop
				if line else line for line in text]
	else:
		text_res = [comment_start + after_comment + border * pad_to
				+ after_comment + comment_stop]
		text_res += [comment_start + after_comment + 
				pad_line(line, pad_to) + 
				after_comment + comment_stop
					for line in text]
		text_res += [comment_start + after_comment + border * pad_to
				+ after_comment + comment_stop]
		text = text_res
	return "\n".join(text)


def uncomment_multiline_block_oriented(text, comment_start, comment_stop,
		after_comment = " ", fancy = False,
		border = "*",
		pad_to = 0):
	"""
	Uncomment a text block block oriented.
	"""
	
	text = text.split("\n")
	max_length = len(max(text, key = lambda x: len(x)))

	if(max_length > pad_to):
		pad_to = max_length

	indent = " " * (len(comment_start) - 1) + border


	text_res = [comment_start + after_comment + border * pad_to
			+ after_comment + border]
	text_res += [indent + after_comment + pad_line(line, pad_to) + 
			after_comment + border 
				for line in text]
	text_res += [indent + after_comment + border * pad_to
			+ after_comment + comment_stop]
	text = text_res

	return "\n".join(text)
