#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

# <pep8 compliant>

import bpy

from ...utils import copy_bone
from ...utils import strip_org, make_deformer_name
from ...utils import create_bone_widget, create_circle_widget


class Rig:
    """ A "copy" rig.  All it does is duplicate the original bone and
        constrain it.
        This is a control and deformation rig.

    """
    def __init__(self, obj, bone, params):
        """ Gather and validate data about the rig.
        """
        self.obj          = obj
        self.org_bone     = bone
        self.org_name     = strip_org(bone)
        self.params       = params
        self.make_control = params.make_control
        self.make_widget  = params.make_widget
        self.make_deform  = params.make_deform

    def generate(self):
        """ Generate the rig.
            Do NOT modify any of the original bones, except for adding constraints.
            The main armature should be selected and active before this is called.

        """
        bpy.ops.object.mode_set(mode='EDIT')

        # Make a control bone (copy of original).
        if self.make_control:
            bone = copy_bone(self.obj, self.org_bone, self.org_name)

        # Make a deformation bone (copy of original, child of original).
        if self.make_deform:
            def_bone = copy_bone(self.obj, self.org_bone, make_deformer_name(self.org_name))

        # Get edit bones
        eb = self.obj.data.edit_bones
        # UNUSED
        # if self.make_control:
        #     bone_e = eb[bone]
        if self.make_deform:
            def_bone_e = eb[def_bone]

        # Parent
        if self.make_deform:
            def_bone_e.use_connect = False
            def_bone_e.parent = eb[self.org_bone]

        bpy.ops.object.mode_set(mode='OBJECT')
        pb = self.obj.pose.bones

        if self.make_control:
            # Constrain the original bone.
            con = pb[self.org_bone].constraints.new('COPY_TRANSFORMS')
            con.name = "copy_transforms"
            con.target = self.obj
            con.subtarget = bone

            # Create control widget
            if self.make_widget:
                create_circle_widget(self.obj, bone, radius = 0.5 )
            else:
                create_bone_widget(self.obj, bone, radius = 0.5 )

def add_parameters(params):
    """ Add the parameters of this rig type to the
        RigifyParameters PropertyGroup
    """
    params.make_control = bpy.props.BoolProperty(
        name        = "Control",
        default     = True,
        description = "Create a control bone for the copy"
    )

    params.make_widget = bpy.props.BoolProperty(
        name        = "Widget",
        default     = True,
        description = "Choose a widget for the bone control"
    )

    params.make_deform = bpy.props.BoolProperty(
        name        = "Deform",
        default     = True,
        description = "Create a deform bone for the copy"
    )


def parameters_ui(layout, params):
    """ Create the ui for the rig parameters.
    """
    r = layout.row()
    r.prop(params, "make_control")
    r = layout.row()
    r.prop(params, "make_widget")
    r = layout.row()
    r.prop(params, "make_deform")


def create_sample(obj):
    """ Create a sample metarig for this rig type.
    """
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}

    bone = arm.edit_bones.new('Bone')
    bone.head[:] = 0.0000, 0.0000, 0.0000
    bone.tail[:] = 0.0000, 0.0000, 0.2000
    bone.roll = 0.0000
    bone.use_connect = False
    bones['Bone'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['Bone']]
    pbone.rigify_type = 'basic.copy'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'

    bpy.ops.object.mode_set(mode='EDIT')
    for bone in arm.edit_bones:
        bone.select = False
        bone.select_head = False
        bone.select_tail = False
    for b in bones:
        bone = arm.edit_bones[bones[b]]
        bone.select = True
        bone.select_head = True
        bone.select_tail = True
        arm.edit_bones.active = bone
