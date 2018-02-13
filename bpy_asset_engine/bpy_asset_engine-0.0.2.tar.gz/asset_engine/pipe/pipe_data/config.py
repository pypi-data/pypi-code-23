# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    

:synopsis:
    

:description:
    

:applications:
    
:see_also:
   
:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#

#TODO FIX PREFERENCE IMPORTING
get_prefs = None
# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#



def get_default_config(key=None):
    """
    Get default configuration file based on supplied key
    :param key:
    :return:
    """
    global get_prefs # lazy import
    if get_prefs is None:
        from ...bsetup.preferences import getPreferences as get_prefs
    # Get User Preferences
    preferences = get_prefs()


    if key is not None:
        if key == "project":
            """return Project Directory Structure"""
            pass

        elif key == 'asset':
            """Return Asset Directory Structure"""
            pass

        elif key == 'pipeline':
            """Return Pipeline Directory Structure"""
            pass
    else:
        raise ValueError("'key' arg for method is None. Aborting")


def get_user_config(key=None):
    """
    Get default configuration file based on supplied key
    :param key:
    :return:
    """
    global get_prefs  # lazy import
    if get_prefs is None:
        from ...bsetup.preferences import getPreferences as get_prefs
    # Get User Preferences
    preferences = get_prefs()

    if key is not None:
        if key == "project":
            """return Project Directory Structure"""
            pass

        elif key == 'asset':
            """Return Asset Directory Structure"""
            pass

        elif key == 'pipeline':
            """Return Pipeline Directory Structure"""
            pass
    else:
        raise ValueError("'key' arg for method is None. Aborting")
# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

