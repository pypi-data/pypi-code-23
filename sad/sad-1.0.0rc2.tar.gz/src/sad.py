"""

"""


class CellContainer:
	def __init__(self, sheet):
		self.sheet = sheet    # Pointer to all the spreadsheet data.

	def __len__(self):
		return len(self.cells)

	def __iter__(self):
		self._iter_index = 0    # Reset our index whenever a new loop starts.
		return self

	def __next__(self):
		# Are we at the end?
		if self._iter_index == len(self.cells):
			raise StopIteration
		cells = self.cells
		result = cells[self._iter_index]
		self._iter_index += 1
		return result

	@property
	def cells(self):
		""" A tuple of the cells that this object references. """
		# The cells that apply to this object. By default, the entire spreadsheet.
		# Subclasses need to override as appropriate to point to just the cells that apply to them.
		return self.sheet

	def index_for_column_named(self, name):
		""" Which column has this name? Returns None if not found. """
		# Yes, more Pythonic to raise an exception, but our audience is likely not that advanced.
		for cell_index in range(len(self.sheet[0])):
			if self.sheet[0][cell_index] == name:
				return cell_index

	def index_for_row_named(self, name):
		""" Which row has this header name? Returns None if not found. """
		# Yes, more Pythonic to raise an exception, but our audience is likely not that advanced.
		for index in range(len(self.sheet)):
			if self.sheet[index][0] == name:
				return index


class Spreadsheet(CellContainer):
	@classmethod
	def from_csv(cls, csv_iterable):
		"""
		:param csv_iterable: An iterable that csv.reader() will consume.
		:return: Spreadsheet
		"""
		import csv
		cells = tuple(csv.reader(csv_iterable))
		return cls(cells)

	def column(self, index):
		"""
		:param index: The index of the desired column.
		:return: Column
		"""
		# To keep things simple, for now we don't cache anything.
		# Instead just recreate them on demand.
		return Column(self.sheet, index)

	@property
	def columns(self):
		"""
		Returns a list of Column objects for this spreadsheet.
		:return: list
		"""
		return [self.column(index) for index in range(len(self.cells[0]))]

	def row(self, index):
		"""
		:param index: The index of the desired row.
		:return: Row
		"""
		return Row(self.sheet, index)

	@property
	def rows(self):
		"""
		Returns a list of Row objects for this spreadsheet.
		:return: list
		"""
		return [self.row(index) for index in range(len(self.cells))]

	def __getitem__(self, item):
		# Act as list or dict depending on how they are accessing.
		if isinstance(item, int):
			return self.row(item)
		elif isinstance(item, str):
			header_index = self.index_for_row_named(item)
			if header_index is not None:
				return self.row(header_index)
			else:
				raise KeyError("'{}' not found".format(item))


class Column(CellContainer):
	def __init__(self, sheet, index):
		super().__init__(sheet)
		self.index = index

	@property
	def cells(self):
		"""
		Returns a list of the cells in this column.
		:return: list
		"""
		return [row[self.index] for row in self.sheet]

	def __str__(self):
		return '\n'.join(self.cells)

	def __getitem__(self, item):
		# Act as list or dict depending on how they are accessing.
		if isinstance(item, int):
			return self.cells[item]
		elif isinstance(item, str):
			row_index = self.index_for_row_named(item)
			if row_index is not None:
				return self.cells[row_index]
			else:
				raise KeyError("'{}' not found".format(item))


class Row(CellContainer):
	def __init__(self, sheet, index):
		super().__init__(sheet)
		self.index = index

	@property
	def cells(self):
		"""
		Returns a list of the cells in this row.
		:return: list
		"""
		return self.sheet[self.index]

	def __str__(self):
		return ', '.join(self.cells)

	def __getitem__(self, item):
		# Act as list or dict depending on how they are accessing.
		if isinstance(item, int):
			return self.cells[item]
		elif isinstance(item, str):
			header_index = self.index_for_column_named(item)
			if header_index is not None:
				return self.cells[header_index]
			else:
				raise KeyError("'{}' not found".format(item))
