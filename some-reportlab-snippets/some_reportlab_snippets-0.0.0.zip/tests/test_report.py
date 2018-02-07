# -*- coding: utf-8 -*-

###############################################################################
import numpy as np
import unittest

from some_reportlab_snippets.mplfig import MatplotlibFig
from some_reportlab_snippets.report import Report, User

###############################################################################
class TestReportGeneration(unittest.TestCase):

    def test_00_upper(self):
        report = Report(logo='data\\logo.pdf', title = 'Kantenprofilmessung')
        user = User()

        figsize = (4, 3)
        fig = MatplotlibFig(figsize = figsize)
        
        xBevel = 200.
        yApex = 50.
        alpha = 10.
        t = 400.
    
        alphaRad = alpha * np.pi / 180.
        sinAlpha = np.sin(alphaRad)
        cosAlpha = np.cos(alphaRad)
    
        r = ((t / 2. - yApex) * cosAlpha - xBevel * sinAlpha) / (1. - sinAlpha)
    
        ### SEMI parameters
        sA = 76
        sB = 508
    
        ### upper semi mask
        x = [0, sA]
        y = t/2 + np.array([-sA, 0])
        fig.setData(x, y, 'r')
        
        ### lower semi mask
        x = [51, 51, sB]
        y = t/2 + np.array([-t/2, -t/3, 0])
        fig.addData(x, y, 'r')
    
        ### apex
        x = [0, 0]
        y = [-yApex, yApex]
        fig.addData(x, y)
    
        ### bevel
        xRadius = r - r * sinAlpha
        yBevel = yApex + r * np.cos(alpha * np.pi / 180.)
      
        x = [xRadius, xBevel]
        y = [yBevel, t/2.]
        fig.addData(x, y)
    
        ### radius
        from matplotlib.patches import Arc
        xy = (r, yApex)
        d = 2 * r
        arc = Arc(xy, d, d, angle = 0., theta1 = 100., theta2 = 180.)
    
        fig.addPatch(arc)
    
        ### wafer surface
        x = [xBevel, sB]
        y = [t/2, t/2]
        fig.addData(x, y)
    
        ### symmetry axis
        x = [-50, sB]
        y = [0, 0]
        fig.addData(x, y, '-.k')
        
        
        fig.xlim = (-50, sB)
        fig.ylim = (-100, 250)
        
        parameterPlot = fig.savefig()
    
        report.story = [user, parameterPlot]    
        
        report.save('output\\report.pdf')
