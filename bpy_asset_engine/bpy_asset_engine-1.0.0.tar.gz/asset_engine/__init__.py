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

bl_info = {
    "name": "Asset Engine",
    "author": "Jared Webber",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "",
    "description": "Asset Engine Backend",
    "category": "System",
    "tracker_url": "",
    "wiki_url": ""
}

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#

import os
import sys
# from . import conf
# from . import addon_updater_ops
from .utils.io import IO

# Check for Blender
try:
    import bpy
except ImportError:
    pass

try:
    from .bsetup import developer_utils
except:
    pass
if "developer_utils" not in globals():
    message = ("\n\n"
               "Asset Engine cannot be registered correctly\n"
               "Troubleshooting:\n"
               "  1. Try installing the addon in the newest official Blender version.\n"
               "  2. Try installing the newest Asset Engine version from Gitlab.\n")
    raise Exception(message)

# Import and Reload Submodules
import importlib
from . import developer_utils

importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())


# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

def register_addon():
    """
    Blender specific registration function
    :return:
    """
    # Register Blender Properties and Handlers

    try:
        import pip
    except ImportError:
        IO.info("pip python package not found. Installing.")
        try:
            import ensurepip
            ensurepip.bootstrap(upgrade=True, default_pip=True)
        except ImportError:
            IO.info("pip cannot be configured or installed. ")
    IO.info("Registered Asset Engine")

def unregister_addon():
    """
    Blender specific un-register function
    :return:
    """
    IO.info("Unregistered Asset Engine")


def register():
    """
    Blender specific registration function
    :return:
    """
    register_addon()
    bpy.utils.register_module(__name__)
    for module in modules:
        if hasattr(module, "register"):
            module.register()
    # Register Blender Properties and Handlers
    # addon_updater_ops.register_updater(bl_info)
    # conf.register()


def unregister():
    """
    Blender specific un-register function
    :return:
    """
    bpy.utils.unregister_module(__name__)
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
    # Unregister Blender Properties and Handlers
    # conf.unregister()
    # addon_updater_ops.unregister_updater()
    unregister_addon()

# if __name__ == "__main__":
#     register()


# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

