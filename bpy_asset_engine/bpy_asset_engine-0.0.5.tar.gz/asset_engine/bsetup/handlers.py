# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    

:synopsis:
    Installs required python packages for this addon

:description:
    

:applications:
    
:see_also:
   
:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
# import os
# from os.path import join
# import bpy
# from .. import conf
# from .. utils.io import catch_registration_error, IO, Autovivification
# from .preferences import getPreferences
# import subprocess
# import shutil
# import platform
#
# resource_path = bpy.utils.resource_path('LOCAL',
#                                         major=bpy.app.version[0],
#                                         minor=bpy.app.version[1])
# user_path = bpy.utils.resource_path('USER',
#                                     major=bpy.app.version[0],
#                                     minor=bpy.app.version[1])
# bpy_dir = os.path.join(resource_path, 'python')
# config_dir = os.path.join(user_path, 'scripts/config')
# # ---------------------------------------------------------------------------------------#
# # -------------------------------------------------------------------------- FUNCTIONS --#
#
#
# def run_command_popen(cmd):
#     sp = subprocess.Popen(cmd, stderr=subprocess.PIPE)
#     out, err = sp.communicate()
#     if err:
#         print("__________________________")
#         print("Subprocess standard error:")
#         print(err.decode('ascii'))
#         # sp.wait()
#
# # ---------------------------------------------------------------------------------------#
# # ---------------------------------------------------------------------------- CLASSES --#
#
#
# class InstallRequirements(bpy.types.Operator):
#     bl_idname = "onelvxe_install.bpy_geo_lod_packages"
#     bl_label = "Install Requirements"
#     bl_options = {'REGISTER'}
#
#     def execute(self, context):
#         """Installs requirements.txt and Pysbs"""
#         if conf.py_reqs is True:
#             self.report({'INFO'}, "Addon Package Already Configured")
#             return{'CANCELLED'}
#         else:
#             pass
#         self.report({'INFO'}, "Addon Package Installed. Please Restart Blender.")
#         return {'FINISHED'}
#

# ---------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------- REGISTER --#


