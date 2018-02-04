#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 16:32:13 2018

@author: muenker
"""

    class MplWidget(QWidget):
        """
        Construct a subwidget from pyQt Matplotlib canvas and a modified NavigationToolbar.
        """
        def __init__(self, parent):
            super(MplWidget, self).__init__(parent)
            self.fig = Figure()
    
            self.pltCanv = FigureCanvas(self.fig)
            self.pltCanv.setSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Expanding)
            self.pltCanv.setFocusPolicy(QtCore.Qt.ClickFocus)
            self.pltCanv.setFocus()
            self.pltCanv.updateGeometry()
    
            self.mplToolbar = MplToolbar(self.pltCanv, self)
    
            #=============================================
            # Main plot widget layout
            #=============================================
            self.layVMainMpl = QVBoxLayout()
            self.layVMainMpl.addWidget(self.mplToolbar)
            self.layVMainMpl.addWidget(self.pltCanv)
    
            self.setLayout(self.layVMainMpl)
            
        def redraw(self):
            """
            Redraw the figure with new properties (grid, linewidth)
            """
            # only execute when at least one axis exists -> tight_layout crashes otherwise
            if self.fig.axes:
                for ax in self.fig.axes:
                    if self.mplToolbar.lock_zoom:
                        ax.axis(self.limits) # restore old limits
                    else:
                        self.limits = ax.axis() # save limits
                try:
                    # tight_layout() crashes with small figure sizes e.g. when upper
                    # and lower limits are swapped
                   self.fig.tight_layout(pad = 0.1)
                except(ValueError, np.linalg.linalg.LinAlgError):
                    pass
    
                self.pltCanv.draw() # now (re-)draw the figure
