###########################################################################
# Top30 is Copyright (C) 2016-2018 Kyle Robbertze <krobbertze@gmail.com>
#
# Top30 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Top30 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Top30.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################
from PyQt5 import QtCore, QtWidgets, QtGui

from mutagen.id3 import COMM
import mutagen
import top30

class ClipListModel(QtCore.QAbstractTableModel):
    def __init__(self):
        QtCore.QAbstractTableModel.__init__(self, parent=None)
        self.horizontal_header = ["Type", "Filename", "Start"]
        self.data = []

    def supportedDragActions(self):
        return QtCore.Qt.MoveAction

    def flags(self, index):
        flags = QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable 
        if index.isValid():
            if index.column() == self.columnCount() - 1:
                flags |= QtCore.Qt.ItemIsEditable
            flags |= QtCore.Qt.ItemIsDragEnabled
        return flags

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return self.data[index.row()][index.column()]
        return None

    def setData(self, index, value, role):
        if role != QtCore.Qt.EditRole or not index.isValid() or index.column() != self.columnCount() - 1:
            return False
        if value == "":
            self.data[index.row()][index.column()] = None
            self.data[index.row()][0] = "Voice"
        else:
            self.data[index.row()][0] = "Song"
            if not ":" in value:
                value = "00:" + value
            if value.count(":") > 1:
                return False
            minute = value.split(":")[0]
            second = value.split(":")[1]
            if not is_number(minute) or not is_number(second):
                return False
            value = "{0:02d}:{1:0>4.1f}".format(int(minute), float(second))
            self.data[index.row()][index.column()] = value

        filename = self.data[index.row()][1]
        song_meta = mutagen.File(filename)
        tag = top30.SETTINGS.song_start_tag()
        if top30.get_format(filename) == "mp3":
            comment = COMM(3, "eng", "", value)
            song_meta['COMM:eng'] = comment
        else:
            song_meta[tag] = value
        song_meta.save()
        return True;

    def headerData(self, index, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            return self.horizontal_header[index]
        else:
            return str(index + 1)

    def appendRow(self, row):
        self.insertRows(self.rowCount(),[row])

    def insertRows(self, row, rows, parent = QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + len(rows) - 1)
        for i in range(len(rows)):
            row_i = row + i
            self.data.insert(row_i, rows[i])
        self.endInsertRows()

    def insertRow(self, row, row_data):
        self.insertRows(row, [row_data])

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            del self.data[row + count - 1]
        self.endRemoveRows()
        return True

    def removeRow(self, row):
        self.removeRows(row, 1)

    def moveRows(self, source_parent, source_first, source_last,
            destination_parent, destination):
        # Handle funny crashing bug
        self.beginMoveRows(source_parent, source_first, source_last,
                           destination_parent, destination)
        items = self.data[source_first:source_last + 1]
        self.data = self.data[:source_first] + self.data[source_last + 1:]
        for i in range(len(items)):
            self.data.insert(destination + i, items[i])
        self.endMoveRows()

class ClipListView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        QtWidgets.QTableView.__init__(self, parent=None)
        self.horizontalHeader().setStretchLastSection(True)
        self.resizeColumnsToContents()
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.setDropIndicatorShown(True)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/top30clip') or event.mimeData().hasFormat('audio/ogg') or event.mimeData().hasFormat('audio/mp3'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid() or index.row() == self.source_index.row():
            return
        source = self.source_index.row()
        destination = index.row()
        if destination == source + 1:
            destination = source
            source += 1
        self.model().moveRows(QtCore.QModelIndex(), source, source,
                              QtCore.QModelIndex(), destination)
        event.accept()

    def mousePressEvent(self, event):
        super(ClipListView, self).mousePressEvent(event)
        self.startDrag(event)

    def startDrag(self, event):
        self.source_index = self.indexAt(event.pos())
        if not self.source_index.isValid():
            return

        drag = QtGui.QDrag(self)

        mimeData = QtCore.QMimeData()
        mimeData.setData("application/top30clip", b"")
        drag.setMimeData(mimeData)

        vis = self.source_index.sibling(self.source_index.row() + 1,
                                        self.source_index.column())
        pixmap = QtGui.QPixmap()
        pixmap = self.grab(self.visualRect(vis))
        drag.setPixmap(pixmap)
        result = drag.exec()

def is_number(number):
    try:
        float(number)
        return True
    except ValueError:
        return False
