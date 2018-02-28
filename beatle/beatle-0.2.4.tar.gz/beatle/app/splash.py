# -*- coding: utf-8 -*-
import wx


from beatle.ctx import THE_CONTEXT as context



class AppSplashScreen(wx.SplashScreen):
    """
    Create a splash screen widget.
    """
    
    
    def __init__(self, parent=None):
        """Initialize splash screen"""
        from beatle import localpath
        aBitmap = wx.Image(name=localpath("app/res/beatle.jpg")).ConvertToBitmap()
        splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
        splashDuration = 2000  # milliseconds
        # Call the constructor with the above arguments in exactly the
        # following order.
        wx.SplashScreen.__init__(self, aBitmap, splashStyle,
                                 splashDuration, parent)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.running = True
        wx.YieldIfNeeded()
        

    def OnExit(self, evt):
        """Continue process"""
        from beatle.app import mainWindow
        self.Hide()
        # The program will freeze without this line.
        evt.Skip()  # Make sure the default handler runs too...
        self.running = False
