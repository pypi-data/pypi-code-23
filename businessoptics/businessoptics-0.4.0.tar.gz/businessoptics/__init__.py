# Import everything from client for compatibility
from .client import *

from .cached_file_getter import CachedGoogleDriveFile

#Alias for ease of use
gdrive_file = CachedGoogleDriveFile
