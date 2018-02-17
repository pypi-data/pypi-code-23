# -*- coding: utf-8 -*-
"""QAbstractTableModel for 2D arrays module.

contains PSNumpyModel2D
"""

from PyQt5 import QtCore


class PSNumpyModel2D(QtCore.QAbstractTableModel):

    """Subclass of QAbstractTableModel used to display numpy 2D arrays."""

    def __init__(self, narray, parent=None):
        """Model init.

        Args:
            narray (numpy.ndarray): 2D numpy array
            parent: Parent of the model, passed to QAbstractTableModel.
        """
        super().__init__(parent)
        self.__array = narray

    def getRow(self, index):
        """Return single row.

        Args:
            index (int): Row index.
        Returns:
            One dimensional numpy.ndarray containing the requested row.
        """
        return self.__array[index, :]

    def getColumn(self, index):
        """Return single column.

        Args:
            index (int): Column index.
        Returns:
            One dimensional numpy.ndarray containing the requested column.
        """
        return self.__array[:, index]

    def rowCount(self, parent=None):
        """Return number of rows."""
        return self.__array.shape[0]

    def columnCount(self, parent=None):
        """Return number of columns."""
        return self.__array.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Data at `index`.

        Args:
            index (QModelIndex): Table index.
            role (Qt role): Qt role, defaults to Qt.DisplayRole

        Returns:
            QVariant containing the str(data) at `index`.
        """
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                row = index.row()
                col = index.column()
                return QtCore.QVariant(str(self.getItemAt(row, col)))
        return QtCore.QVariant()

    @property
    def array(self):
        """Numpy array underlying this model."""
        return self.__array

    def getItemAt(self, row, column):
        """Return data at specified row and column.

        Args:
            row (int): Table row.
            column (int): Table column.

        Returns:
            Numpy array element at [row, column]
        """
        return self.__array[row, column]

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Numbers in the header, starting from zero."""
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(section)
        return QtCore.QVariant()
