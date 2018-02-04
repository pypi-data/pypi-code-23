from stellarpy import Star, Body, Make
import sys

au = 149597870


def test():
    SUN = Star('Sun', m=1.98892e30)  # J2000.0 JD2451545.0
    Make(SUN, color=(1, 1, 0, 1))

    MERCURY = Body('Mercury', major=SUN, m=3.33022e23, a=57909227, e=0.20563593, i=7.00487, w=29.124279,
                     O=48.33167, M=174.795884)
    Make(MERCURY, color=(.5, .5, .5, 1))

    VENUS = Body('Venus', major=SUN, m=4.8675e24, a=108209475, e=0.00677323, i=3.39471, w=54.85229,
                   O=76.67069, M=50.115)
    Make(VENUS, color=(0.3, 0, 0, 1))

    EARTH = Body('Earth', major=SUN, m=5.9726e24, a=149598262, e=0.01671022, i=0.00005, w=114.20783,
                   O=348.73936, M=358.617)
    Make(EARTH, color=(0, 0, 1, 1))

    MARS = Body('Mars', major=SUN, m=6.4185e23, a=227943824, e=0.09341233, i=1.85061, w=286.46230,
                  O=49.57854, M=19.373)
    Make(MARS, color=(1, 0, 0, 1))

    JUPITER = Body('Jupiter', major=SUN, m=1.8986e27, a=778340821, e=0.04839266, i=1.30530, w=275.066,
                     O=100.55615, M=20.020)
    Make(JUPITER, color=(.5, .5, 0, 1))

    SATURN = Body('Saturn', major=SUN, m=5.6846e26, a=1433449370, e=0.055723219, i=2.485240, w=336.013862,
                    O=113.71504, M=317.020)
    Make(SATURN, color=(1, 1, 0, 1))

    URANUS = Body('Uranus', major=SUN, m=8.6832e25, a=2870658186, e=0.04716771, i=0.76986, w=96.541318,
                    O=74.22988, M=142.238600)
    Make(URANUS, color=(0, 0.5, 0, 1))

    NEPTUNE = Body('Neptune', major=SUN, m=1.0243e26, a=4498396441, e=0.00858587, i=1.76917, w=265.646853,
                     O=131.72169, M=256.228)
    Make(NEPTUNE, color=(0, 0, .5, 1))

    CARES = Body('Ceres', major=SUN, m=9.393e20, a=413767000, e=0.07934, i=10.585, w=2.825, O=80.399,
                   M=27.448, JD=2455000.5)
    Make(CARES, color=(.5, .5, .5, 1))

    PLUTO = Body('Pluto', major=SUN, m=1.303e22, a=5906440628, e=0.24880766, i=17.14175, w=113.76329,
                   O=110.30347, M=14.53, JD=2451545.0)
    Make(PLUTO, color=(0.3, 0, 0, 1))

    HAUMEA = Body('Haumea', major=SUN, m=4.006e21, a=42.98492 * au, e=0.1975233, i=28.201975,
                    w=240.582838, O=121.900456, M=205.22317, JD=2456000.5)
    Make(HAUMEA, color=(.5, .5, .5, 1))

    MAKEMAKE = Body('Makemake', major=SUN, m=3e21, a=45.436301 * au, e=0.16254481, i=29.011819,
                      w=296.534594, O=79.305348, M=153.854714, JD=2456000.5)
    Make(MAKEMAKE, color=(0.3, 0, 0, 1))

    ERIS = Body('Eris', major=SUN, m=1.66e22, a=67.781 * au, e=0.44068, i=44.0445, w=150.977, O=35.9531,
                  M=204.16, JD=2457000.5)
    Make(ERIS, color=(.5, .5, .5, 1))

    SEDNA = Body('Sedna', major=SUN, m=8.3e21, a=541.429506 * au, e=0.8590486, i=11.927945, w=310.920993,
                   O=144.377238, M=358.190921, JD=2456000.5)
    Make(SEDNA, color=(1, 1, 1, 1))

    from pyqtgraph.Qt import QtCore, QtGui
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()