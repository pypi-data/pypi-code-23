'''
--------------------------------------------------------------------------
Copyright (C) 2017-2018 Lukasz Laba <lukaszlab@o2.pl>

This file is part of Tebe.

Tebe is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Tebe is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

from PyQt4 import QtGui, QtCore, QtWebKit

class Preview(QtWebKit.QWebView):
	def __init__(self, parent=None):
		super(Preview, self).__init__(parent)
		self.settings().setObjectCacheCapacities(0,0,0) #it's responsible for refreshing images
		#---
		self.scroll_fixed_position = False
		#---
		self.page().mainFrame().loadFinished.connect(self.scroll_to_fixed_position)
		
	def show_html(self, path):
		self.load(QtCore.QUrl.fromLocalFile(path))

	def show_url(self, link):
		self.load(QtCore.QUrl(link))
		
	def scroll_fix(self):
		if self.page().mainFrame().scrollPosition().y() != 0:
			self.scroll_fixed_position = self.scroll_get_position()
	
	def scroll_get_position(self):
		return self.page().mainFrame().scrollPosition().y()
		
	def scroll_up(self):
		self.scroll_fixed_position = 1
		self.scroll_to_fixed_position()
	
	def scroll_to_fixed_position(self):
		if self.scroll_fixed_position:
			self.scroll_to_absposition(self.scroll_fixed_position)

	def scroll_to_absposition(self, position):
		point = QtCore.QPoint(0, position)
		self.scroll_fixed_position = position
		self.page().mainFrame().setScrollPosition(point)

	def scroll_to_relposition(self, relosition):
		absposition = relosition * self.page().mainFrame().scrollBarMaximum(QtCore.Qt.Vertical) 
		self.scroll_to_absposition(absposition)