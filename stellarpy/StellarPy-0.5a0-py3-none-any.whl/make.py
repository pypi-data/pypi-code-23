#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
from numpy import vstack, array

# настройки окна
app = QtGui.QApplication([])

plot_wid = gl.GLViewWidget()
plot_wid.setWindowTitle('Planet System beta')
plot_wid.setGeometry(200, 50, 1024, 768)
plot_wid.setBackgroundColor('w')
plot_wid.opts['distance'] = 50000000000
plot_wid.orbit(-90, 10)
plot_wid.show()

# ось эклиптики (сетка)
g = gl.GLGridItem(color=[0, 0, 1, .1])
g.setSize(x=50000000000, y=50000000000)
g.setSpacing(x=700000000, y=700000000)
plot_wid.addItem(g)

# точка овна
pts_ARIES = vstack([(0, 2e10), (0, 0), (0, 0)]).transpose()
ARIES_p = gl.GLLinePlotItem(pos=pts_ARIES, width=0.1, color=(1, 0, 0, 1), antialias=True)
plot_wid.addItem(ARIES_p)
# ARIES_t = ax.text(2e10, 0, 0, 'Aries', color='r', alpha=0.5)


class Make:
    def __init__(self, body, color=None, orbit=True, guide=True):
        """
        :param class body: объект
        """
        self.size = 10
        self.width = 1
        self.color = color if color is not None else (.5, .5, .5, 1)
        self.set_size(body.m)
        self.orbit = orbit
        self.guide = guide
        self.X = body.X
        self.Y = body.Y
        self.Z = body.Z
        self.pos = None
        self.way = None
        self.orb = None
        self.paint()

    def set_size(self, m=1e23, size=None, width=None):
        if m > 1.5e+29:
            self.size = 10
        elif m > 1e25:
            self.size = 10
            self.width = 1
        elif m > 1e23:
            self.size = 8
            self.width = 1
        elif m > 1e20:
            self.size = 6
            self.width = 1
        else:
            self.size = 1.5
            self.width = .25

    def paint(self):
        self.pos = gl.GLScatterPlotItem(pos=array([self.X[-1], self.Y[-1], self.Z[-1]]), size=self.size, color=self.color)
        self.pos.setGLOptions('translucent')
        plot_wid.addItem(self.pos)
        pts_way = vstack([(self.X[-1], self.X[-1]), (self.Y[-1], self.Y[-1]), (self.Z[-1], 0)]).transpose()
        self.way = gl.GLLinePlotItem(pos=pts_way, width=0.1, color=(0, 0, 0, .5), antialias=True)
        plot_wid.addItem(self.way) if self.guide else None
        pts_orb = vstack([self.X, self.Y, self.Z]).transpose()
        self.orb = gl.GLLinePlotItem(pos=pts_orb, width=self.width, color=(0, 0, 0, 1), antialias=True)
        plot_wid.addItem(self.orb) if self.orbit else None


# if __name__ == '__main__':
#     if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#         QtGui.QApplication.instance().exec_()

    # sys.exit(app.exec_())
