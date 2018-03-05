"""
evoke multi-app server script, for Twisted 
"""

#fix the path - some servers need this...
import os, sys
sys.path.append(os.path.abspath('.'))  
from config_multi import app_module_path
sys.path.append(os.path.abspath(app_module_path))


from twisted.application import service
from evoke.serve import start
from config_multi import apps

## Twisted requires the creation of the root-level application object to take place in this file
application = service.Application("evoke application")
## stitch it all together...
start(application, apps)
