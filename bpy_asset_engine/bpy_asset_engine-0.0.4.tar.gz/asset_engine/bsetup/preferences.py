# import bpy
# from bpy.props import *
#
#
# addonName = "moros"
#
# class PipelinePreferences(bpy.types.AddonPreferences):
#     bl_idname = addonName
#
#     pipe_base_dir = bpy.props.StringProperty(
#         name='Pipeline Base Directory',
#         default='',
#         subtype='DIR_PATH',
#     )
#
#
#     def draw(self, context):
#         preferences = getPreferences()
#         layout = self.layout
#         # Base Pipeline Directory
#         row = layout.row()
#         row.prop(preferences, "pipe_base_dir", text="Pipeline Base Directory")
#         row = layout.row()
#         row.operator('test.operator')
#
# def getPreferences():
#     return bpy.context.user_preferences.addons["moros"].preferences

