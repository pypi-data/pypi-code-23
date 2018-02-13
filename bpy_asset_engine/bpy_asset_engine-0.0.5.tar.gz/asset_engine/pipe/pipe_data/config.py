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

preferences = None
from ...utils.io import IO
# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#



def get_default_config(key=None, **kwargs):
    """
    Get default configuration file based on supplied key
    :param key:
    :return:
    """
    global preferences
    IO.debug("Generating User Preferences")
    if preferences is None:
        import bpy
        if kwargs.get('addon_name') is None:
            # Default to Moros addon
            preferences = bpy.context.user_preferences.addons["moros"].preferences

        else:
            preferences = bpy.context.user_preferences.addons[
                kwargs.get("addon_name")].preferences

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


def get_user_config(key=None, **kwargs):
    """
    Get default configuration file based on supplied key
    :param key:
    :return:
    """
    global preferences
    IO.debug("Generating User Preferences")
    if preferences is None:
        import bpy
        if kwargs.get('addon_name') is None:
            # Default to Moros addon
            preferences = bpy.context.user_preferences.addons["moros"].preferences

        else:
            preferences = bpy.context.user_preferences.addons[
                kwargs.get("addon_name")].preferences

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

