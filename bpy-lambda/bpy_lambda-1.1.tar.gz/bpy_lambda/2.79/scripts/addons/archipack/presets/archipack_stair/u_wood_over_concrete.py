import bpy
d = bpy.context.active_object.data.archipack_stair[0]

d.steps_type = 'CLOSED'
d.handrail_slice_right = True
d.total_angle = 6.2831854820251465
d.user_defined_subs_enable = True
d.string_z = 0.30000001192092896
d.nose_z = 0.029999999329447746
d.user_defined_subs = ''
d.idmat_step_side = '3'
d.handrail_x = 0.03999999910593033
d.right_post = True
d.left_post = True
d.width = 1.5
d.subs_offset_x = 0.0
d.rail_mat.clear()
item_sub_1 = d.rail_mat.add()
item_sub_1.name = ''
item_sub_1.index = '4'
d.step_depth = 0.30000001192092896
d.rail_z = (0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806)
d.right_subs = False
d.left_panel = True
d.idmat_handrail = '3'
d.da = 3.1415927410125732
d.post_alt = 0.0
d.left_subs = False
d.n_parts = 3
d.user_defined_post_enable = True
d.handrail_slice_left = True
d.handrail_profil = 'SQUARE'
d.handrail_expand = False
d.panel_alt = 0.25
d.post_expand = False
d.subs_z = 1.0
d.rail_alt = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
d.panel_dist = 0.05000000074505806
d.panel_expand = False
d.x_offset = 0.0
d.subs_expand = False
d.idmat_post = '4'
d.left_string = False
d.string_alt = -0.03999999910593033
d.handrail_y = 0.03999999910593033
d.radius = 1.0
d.string_expand = False
d.post_z = 1.0
d.idmat_top = '3'
d.idmat_bottom = '1'
d.parts.clear()
item_sub_1 = d.parts.add()
item_sub_1.name = ''
item_sub_1.manipulators.clear()
item_sub_2 = item_sub_1.manipulators.add()
item_sub_2.name = ''
item_sub_2.p0 = (0.0, 0.0, 0.7875000238418579)
item_sub_2.prop1_name = 'length'
item_sub_2.p2 = (1.0, 0.0, 0.0)
item_sub_2.normal = (0.0, 0.0, 1.0)
item_sub_2.pts_mode = 'SIZE'
item_sub_2.p1 = (0.0, 2.0, 0.7875000238418579)
item_sub_2.prop2_name = 'radius'
item_sub_2.type_key = 'SIZE'
item_sub_1.right_shape = 'RECTANGLE'
item_sub_1.radius = 0.699999988079071
item_sub_1.type = 'S_STAIR'
item_sub_1.length = 2.0
item_sub_1.left_shape = 'RECTANGLE'
item_sub_1.da = 1.5707963705062866
item_sub_1 = d.parts.add()
item_sub_1.name = ''
item_sub_1.manipulators.clear()
item_sub_2 = item_sub_1.manipulators.add()
item_sub_2.name = ''
item_sub_2.p0 = (-1.0, 2.0, 1.912500023841858)
item_sub_2.prop1_name = 'da'
item_sub_2.p2 = (-1.0, -1.1920928955078125e-07, 0.0)
item_sub_2.normal = (0.0, 0.0, 1.0)
item_sub_2.pts_mode = 'RADIUS'
item_sub_2.p1 = (1.0, 0.0, 0.0)
item_sub_2.prop2_name = 'radius'
item_sub_2.type_key = 'ARC_ANGLE_RADIUS'
item_sub_1.right_shape = 'RECTANGLE'
item_sub_1.radius = 0.699999988079071
item_sub_1.type = 'D_STAIR'
item_sub_1.length = 2.0
item_sub_1.left_shape = 'RECTANGLE'
item_sub_1.da = 1.5707963705062866
item_sub_1 = d.parts.add()
item_sub_1.name = ''
item_sub_1.manipulators.clear()
item_sub_2 = item_sub_1.manipulators.add()
item_sub_2.name = ''
item_sub_2.p0 = (-2.0, 1.9999998807907104, 2.700000047683716)
item_sub_2.prop1_name = 'length'
item_sub_2.p2 = (1.0, 0.0, 0.0)
item_sub_2.normal = (0.0, 0.0, 1.0)
item_sub_2.pts_mode = 'SIZE'
item_sub_2.p1 = (-1.9999998807907104, -1.1920928955078125e-07, 2.700000047683716)
item_sub_2.prop2_name = ''
item_sub_2.type_key = 'SIZE'
item_sub_1.right_shape = 'RECTANGLE'
item_sub_1.radius = 0.699999988079071
item_sub_1.type = 'S_STAIR'
item_sub_1.length = 2.0
item_sub_1.left_shape = 'RECTANGLE'
item_sub_1.da = 1.5707963705062866
d.subs_bottom = 'STEP'
d.user_defined_post = ''
d.panel_offset_x = 0.0
d.idmat_side = '1'
d.right_string = False
d.idmat_raise = '1'
d.left_rail = False
d.parts_expand = False
d.panel_z = 0.6000000238418579
d.bottom_z = 0.029999999329447746
d.z_mode = 'STANDARD'
d.panel_x = 0.009999999776482582
d.post_x = 0.03999999910593033
d.presets = 'STAIR_U'
d.steps_expand = True
d.subs_x = 0.019999999552965164
d.subs_spacing = 0.10000000149011612
d.left_handrail = True
d.handrail_offset = 0.0
d.right_rail = False
d.idmat_panel = '5'
d.post_offset_x = 0.019999999552965164
d.idmat_step_front = '3'
d.rail_n = 1
d.string_offset = 0.0
d.subs_y = 0.019999999552965164
d.handrail_alt = 1.0
d.post_corners = False
d.rail_expand = False
d.rail_offset = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
d.rail_x = (0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806, 0.05000000074505806)
d.left_shape = 'RECTANGLE'
d.nose_y = 0.019999999552965164
d.nose_type = 'STRAIGHT'
d.handrail_extend = 0.10000000149011612
d.idmat_string = '3'
d.post_y = 0.03999999910593033
d.subs_alt = 0.0
d.right_handrail = True
d.idmats_expand = False
d.right_shape = 'RECTANGLE'
d.idmat_subs = '4'
d.handrail_radius = 0.019999999552965164
d.right_panel = True
d.post_spacing = 1.0
d.string_x = 0.019999999552965164
d.height = 2.700000047683716
