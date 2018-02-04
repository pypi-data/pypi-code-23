from stellarpy import Star, Body, Make

SUN = Star('Sun', m=1.98892e30)
Make(SUN, color=(1, 1, 0, 1))

MERCURY = Body('Mercury', major=SUN, m=3.33022e23, at=0.0005861,
               a=57909227, e=0.20563593, i=7.00487, w=29.124279, O=48.33167, M=174.795884)
Make(MERCURY, color=(.5, .5, .5, 1))

if __name__ == '__main__':
    from pyqtgraph.Qt import QtCore, QtGui
    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
