import os

# remove conficts beetween IM and wx
if 'GTK_IM_MODULE' in os.environ:
    del os.environ['GTK_IM_MODULE']


import beatle
appInstance = beatle.app.proCxx(0)
appInstance.MainLoop()
