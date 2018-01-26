# ##### BEGIN GPL LICENSE BLOCK #####
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
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import re
from math import cos, pi

import bpy

from ...utils import MetarigError
from ...utils import copy_bone
from ...utils import strip_org, deformer
from ...utils import create_widget


def bone_siblings(obj, bone):
    """ Returns a list of the siblings of the given bone.
        This requires that the bones has a parent.

    """
    parent = obj.data.bones[bone].parent

    if parent is None:
        return []

    bones = []

    for b in parent.children:
        if b.name != bone:
            bones += [b.name]

    return bones


def bone_distance(obj, bone1, bone2):
    """ Returns the distance between two bones.

    """
    vec = obj.data.bones[bone1].head - obj.data.bones[bone2].head
    return vec.length


class Rig:
    """ A "palm" rig.  A set of sibling bones that bend with each other.
        This is a control and deformation rig.

    """
    def __init__(self, obj, bone, params):
        """ Gather and validate data about the rig.
        """
        self.obj = obj
        self.params = params

        siblings = bone_siblings(obj, bone)

        if len(siblings) == 0:
            raise MetarigError(
                    "RIGIFY ERROR: Bone '%s': must have a parent and at least one sibling" %
                    (strip_org(bone)))

        # Sort list by name and distance
        siblings.sort()
        siblings.sort(key=lambda b: bone_distance(obj, bone, b))

        self.org_bones = [bone] + siblings

        # Get rig parameters
        self.palm_rotation_axis = params.palm_rotation_axis

    def generate(self):
        """ Generate the rig.
            Do NOT modify any of the original bones, except for adding constraints.
            The main armature should be selected and active before this is called.

        """
        bpy.ops.object.mode_set(mode='EDIT')

        # Figure out the name for the control bone (remove the last .##)
        last_bone = self.org_bones[-1:][0]
        ctrl_name = re.sub("([0-9]+\.)", "", strip_org(last_bone)[::-1], count=1)[::-1]

        # Make control bone
        ctrl = copy_bone(self.obj, last_bone, ctrl_name)

        # Make deformation bones
        def_bones = []
        for bone in self.org_bones:
            b = copy_bone(self.obj, bone, deformer(strip_org(bone)))
            def_bones += [b]

        # Parenting
        eb = self.obj.data.edit_bones

        # turn off inherit scale for all ORG-bones to prevent undesired transformations

        for o in self.org_bones:
            eb[o].use_inherit_scale = False

        for d, b in zip(def_bones, self.org_bones):
            eb[d].use_connect = False
            eb[d].parent = eb[b]

        # Get ORG parent bone
        org_parent = eb[self.org_bones[0]].parent.name

        # Get DEF parent from ORG parent
        def_parent = deformer(strip_org(org_parent))

        # Switch parent
        if def_parent in eb.keys():
            parent_to = def_parent
        else:
            parent_to = org_parent
        for o in self.org_bones:
            eb[o].parent = eb[parent_to]
        eb[ctrl].parent = eb[parent_to]

        # Constraints
        bpy.ops.object.mode_set(mode='OBJECT')
        pb = self.obj.pose.bones

        i = 0
        div = len(self.org_bones) - 1
        for b in self.org_bones:
            con = pb[b].constraints.new('COPY_TRANSFORMS')
            con.name = "copy_transforms"
            con.target = self.obj
            con.subtarget = ctrl
            con.target_space = 'LOCAL'
            con.owner_space = 'LOCAL'
            con.influence = i / div

            con = pb[b].constraints.new('COPY_SCALE')
            con.name = "copy_scale"
            con.target = self.obj
            con.subtarget = parent_to
            con.target_space = 'WORLD'
            con.owner_space = 'WORLD'
            con.influence = 1

            con = pb[b].constraints.new('COPY_ROTATION')
            con.name = "copy_rotation"
            con.target = self.obj
            con.subtarget = ctrl
            con.target_space = 'LOCAL'
            con.owner_space = 'LOCAL'
            if 'X' in self.palm_rotation_axis:
                con.invert_x = True
                con.use_x = True
                con.use_z = False
            else:
                con.invert_z = True
                con.use_x = False
                con.use_z = True
            con.use_y = False

            con.influence = (i / div) - (1 - cos((i * pi / 2) / div))

            i += 1

        # Create control widget
        w = create_widget(self.obj, ctrl)
        if w is not None:
            mesh = w.data
            verts = [
                (0.1578, 0.0, -0.3),
                (0.1578, 1.0, -0.2),
                (-0.1578, 1.0, -0.2),
                (-0.1578, -0.0, -0.3),
                (-0.1578, -0.0, 0.3),
                (-0.1578, 1.0, 0.2),
                (0.1578, 1.0, 0.2),
                (0.1578, 0.0, 0.3),
                (0.1578, 0.25, -0.275),
                (-0.1578, 0.25, -0.275),
                (0.1578, 0.75, -0.225),
                (-0.1578, 0.75, -0.225),
                (0.1578, 0.75, 0.225),
                (0.1578, 0.25, 0.275),
                (-0.1578, 0.25, 0.275),
                (-0.1578, 0.75, 0.225),
                ]

            if 'Z' in self.palm_rotation_axis:
                # Flip x/z coordinates
                verts = [v[::-1] for v in verts]

            edges = [
                (1, 2), (0, 3), (4, 7), (5, 6),
                (8, 0), (9, 3), (10, 1), (11, 2),
                (12, 6), (13, 7), (4, 14), (15, 5),
                (10, 8), (11, 9), (15, 14), (12, 13),
                ]
            mesh.from_pydata(verts, edges, [])
            mesh.update()

            mod = w.modifiers.new("subsurf", 'SUBSURF')
            mod.levels = 2


def add_parameters(params):
    """ Add the parameters of this rig type to the
        RigifyParameters PropertyGroup

    """
    items = [('X', 'X', ''), ('Z', 'Z', '')]
    params.palm_rotation_axis = bpy.props.EnumProperty(
            items=items,
            name="Palm Rotation Axis",
            default='X',
            )


def parameters_ui(layout, params):
    """ Create the ui for the rig parameters.

    """
    r = layout.row()
    r.label(text="Primary rotation axis:")
    r.prop(params, "palm_rotation_axis", text="")


def create_sample(obj):
    # generated by rigify.utils.write_metarig
    bpy.ops.object.mode_set(mode='EDIT')
    arm = obj.data

    bones = {}

    bone = arm.edit_bones.new('palm.parent')
    bone.head[:] = 0.0000, 0.0000, 0.0000
    bone.tail[:] = 0.0577, 0.0000, -0.0000
    bone.roll = 3.1416
    bone.use_connect = False
    bones['palm.parent'] = bone.name
    bone = arm.edit_bones.new('palm.04')
    bone.head[:] = 0.0577, 0.0315, -0.0000
    bone.tail[:] = 0.1627, 0.0315, -0.0000
    bone.roll = 3.1416
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['palm.parent']]
    bones['palm.04'] = bone.name
    bone = arm.edit_bones.new('palm.03')
    bone.head[:] = 0.0577, 0.0105, -0.0000
    bone.tail[:] = 0.1627, 0.0105, -0.0000
    bone.roll = 3.1416
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['palm.parent']]
    bones['palm.03'] = bone.name
    bone = arm.edit_bones.new('palm.02')
    bone.head[:] = 0.0577, -0.0105, -0.0000
    bone.tail[:] = 0.1627, -0.0105, -0.0000
    bone.roll = 3.1416
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['palm.parent']]
    bones['palm.02'] = bone.name
    bone = arm.edit_bones.new('palm.01')
    bone.head[:] = 0.0577, -0.0315, -0.0000
    bone.tail[:] = 0.1627, -0.0315, -0.0000
    bone.roll = 3.1416
    bone.use_connect = False
    bone.parent = arm.edit_bones[bones['palm.parent']]
    bones['palm.01'] = bone.name

    bpy.ops.object.mode_set(mode='OBJECT')
    pbone = obj.pose.bones[bones['palm.parent']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, False, False)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'QUATERNION'
    pbone = obj.pose.bones[bones['palm.04']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, True, True)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'YXZ'
    pbone = obj.pose.bones[bones['palm.03']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, True, True)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'YXZ'
    pbone = obj.pose.bones[bones['palm.02']]
    pbone.rigify_type = ''
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, True, True)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'YXZ'
    pbone = obj.pose.bones[bones['palm.01']]
    pbone.rigify_type = 'limbs.super_palm'
    pbone.lock_location = (False, False, False)
    pbone.lock_rotation = (False, True, True)
    pbone.lock_rotation_w = False
    pbone.lock_scale = (False, False, False)
    pbone.rotation_mode = 'YXZ'

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
