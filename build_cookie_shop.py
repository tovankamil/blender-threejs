import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Euler, Matrix
import random

def create_cookie_shop():
    # ---------------------------------------------------------
    # 1. Clean existing scene
    # ---------------------------------------------------------
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Remove orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)
            
    # Collection
    scene = bpy.context.scene
    coll = bpy.data.collections.new("CookieShop_World")
    scene.collection.children.link(coll)
    
    def link_obj(obj):
        if obj.name in scene.collection.objects:
            scene.collection.objects.unlink(obj)
        if obj.name not in coll.objects:
            coll.objects.link(obj)
        return obj

    # ---------------------------------------------------------
    # 2. Materials Setup
    # ---------------------------------------------------------
    def get_or_create_mat(name, color, roughness=0.5, metallic=0.0, emission=None, emission_strength=1.0, transmission=0.0, alpha=1.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        
        node_bsdf.inputs['Base Color'].default_value = color
        node_bsdf.inputs['Roughness'].default_value = roughness
        node_bsdf.inputs['Metallic'].default_value = metallic
        
        if 'Transmission Weight' in node_bsdf.inputs:
            node_bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in node_bsdf.inputs:
            node_bsdf.inputs['Transmission'].default_value = transmission
            
        if 'Alpha' in node_bsdf.inputs:
            node_bsdf.inputs['Alpha'].default_value = alpha
            
        if emission:
            if 'Emission Color' in node_bsdf.inputs:
                node_bsdf.inputs['Emission Color'].default_value = emission
                node_bsdf.inputs['Emission Strength'].default_value = emission_strength
            elif 'Emission' in node_bsdf.inputs:
                node_bsdf.inputs['Emission'].default_value = emission
                if 'Emission Strength' in node_bsdf.inputs:
                    node_bsdf.inputs['Emission Strength'].default_value = emission_strength
                    
        mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
        
        if alpha < 1.0 or transmission > 0:
            if hasattr(mat, 'blend_method'):
                mat.blend_method = 'BLEND'
            if hasattr(mat, 'shadow_method'):
                mat.shadow_method = 'NONE'
        return mat

    # Harmonious Pastel & Bakery Palette
    mat_mint = get_or_create_mat("Mat_MintWall", (0.50, 0.78, 0.70, 1.0), roughness=0.55)
    mat_cream = get_or_create_mat("Mat_CreamTrim", (0.96, 0.93, 0.86, 1.0), roughness=0.45)
    mat_pink = get_or_create_mat("Mat_PastelPink", (0.96, 0.58, 0.68, 1.0), roughness=0.45)
    mat_dark_pink = get_or_create_mat("Mat_DarkPink", (0.88, 0.42, 0.52, 1.0), roughness=0.45)
    mat_awning_coral = get_or_create_mat("Mat_AwningCoral", (0.92, 0.35, 0.40, 1.0), roughness=0.55)
    mat_awning_cream = get_or_create_mat("Mat_AwningCream", (0.98, 0.96, 0.90, 1.0), roughness=0.55)
    mat_dough = get_or_create_mat("Mat_CookieDough", (0.83, 0.56, 0.28, 1.0), roughness=0.85)
    mat_choc = get_or_create_mat("Mat_DarkChocolate", (0.08, 0.05, 0.03, 1.0), roughness=0.25, metallic=0.0)
    mat_glass = get_or_create_mat("Mat_WindowGlass", (0.88, 0.95, 1.0, 0.30), roughness=0.05, transmission=0.85, alpha=0.30)
    mat_glow = get_or_create_mat("Mat_InteriorGlow", (1.0, 0.85, 0.50, 1.0), roughness=0.2, emission=(1.0, 0.85, 0.50, 1.0), emission_strength=4.0)
    mat_wood_sign = get_or_create_mat("Mat_WoodSign", (0.22, 0.13, 0.08, 1.0), roughness=0.6)
    mat_gold_text = get_or_create_mat("Mat_GoldText", (1.0, 0.86, 0.38, 1.0), roughness=0.25, metallic=0.75, emission=(1.0, 0.86, 0.38, 1.0), emission_strength=1.5)
    mat_sidewalk = get_or_create_mat("Mat_Sidewalk", (0.76, 0.74, 0.71, 1.0), roughness=0.8)
    mat_curb = get_or_create_mat("Mat_Curb", (0.62, 0.60, 0.58, 1.0), roughness=0.75)
    mat_road = get_or_create_mat("Mat_Road", (0.22, 0.23, 0.26, 1.0), roughness=0.9)
    mat_road_line = get_or_create_mat("Mat_RoadLine", (0.95, 0.92, 0.80, 1.0), roughness=0.8)
    mat_brass = get_or_create_mat("Mat_Brass", (0.92, 0.74, 0.28, 1.0), roughness=0.2, metallic=0.9)
    mat_dark_iron = get_or_create_mat("Mat_DarkIron", (0.18, 0.18, 0.20, 1.0), roughness=0.4, metallic=0.8)
    mat_leaf = get_or_create_mat("Mat_Foliage", (0.32, 0.62, 0.32, 1.0), roughness=0.7)
    mat_flower_pink = get_or_create_mat("Mat_FlowerPink", (0.98, 0.40, 0.62, 1.0), roughness=0.4)
    mat_flower_yellow = get_or_create_mat("Mat_FlowerYellow", (1.0, 0.85, 0.20, 1.0), roughness=0.4)
    mat_chalkboard = get_or_create_mat("Mat_Chalkboard", (0.14, 0.15, 0.16, 1.0), roughness=0.85)
    mat_coir = get_or_create_mat("Mat_DoorMat", (0.62, 0.44, 0.28, 1.0), roughness=0.9)
    mat_frosting = get_or_create_mat("Mat_PinkFrosting", (0.98, 0.52, 0.70, 1.0), roughness=0.35)

    # Mesh creation helpers
    def make_box(name, loc, size, mat=None):
        bpy.ops.mesh.primitive_cube_add(location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = (size[0]/2, size[1]/2, size[2]/2)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if mat:
            obj.data.materials.append(mat)
        return link_obj(obj)

    def make_cylinder(name, loc, r, h, segs=16, mat=None, rot=(0,0,0)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=segs, radius=r, depth=h, location=loc, rotation=rot)
        obj = bpy.context.active_object
        obj.name = name
        if mat:
            obj.data.materials.append(mat)
        return link_obj(obj)

    # ---------------------------------------------------------
    # 3. Sidewalk & Street Ground
    # ---------------------------------------------------------
    # Road (Asphalt)
    make_box("Road", (0, 5.0, 0.01), (18.0, 3.6, 0.02), mat_road)
    # White dashed road line
    for rx in [-6.0, -3.0, 0.0, 3.0, 6.0]:
        make_box(f"RoadLine_{rx}", (rx, 5.4, 0.025), (1.5, 0.15, 0.01), mat_road_line)
    
    # Sidewalk slab (elevated)
    make_box("Sidewalk", (0, 1.6, 0.10), (16.0, 3.2, 0.20), mat_sidewalk)
    # Curb stone rim
    make_box("Curb_Rim", (0, 3.25, 0.11), (16.0, 0.16, 0.22), mat_curb)
    
    # Paving stone score lines
    for x in [-6.0, -4.5, -3.0, -1.5, 0.0, 1.5, 3.0, 4.5, 6.0]:
        make_box(f"PaveLine_V_{x}", (x, 1.6, 0.205), (0.03, 3.15, 0.01), mat_curb)
    make_box("PaveLine_H", (0, 1.6, 0.205), (15.8, 0.03, 0.01), mat_curb)

    # ---------------------------------------------------------
    # 4. Building Architecture
    # ---------------------------------------------------------
    # Building Base Plinth (Cream Stone)
    make_box("Building_Plinth", (0, -1.75, 0.35), (5.8, 3.6, 0.30), mat_cream)
    
    # Main Building Shell (Pastel Mint Wall)
    # Placed back so facade elements sit cleanly on the front (Y = 0)
    make_box("Building_Main", (0, -1.8, 2.5), (5.5, 3.5, 4.0), mat_mint)
    
    # Corner Pilasters / Columns (Cream White)
    make_box("Pillar_L", (-2.7, 0.02, 2.45), (0.38, 0.45, 4.0), mat_cream)
    make_box("Pillar_R", (2.7, 0.02, 2.45), (0.38, 0.45, 4.0), mat_cream)
    make_box("PillarCap_L", (-2.7, 0.02, 4.45), (0.48, 0.55, 0.15), mat_cream)
    make_box("PillarCap_R", (2.7, 0.02, 4.45), (0.48, 0.55, 0.15), mat_cream)

    # Roof Cornice & Stylized Parapet
    make_box("Cornice_Lower", (0, 0.05, 4.38), (5.9, 0.50, 0.14), mat_cream)
    # Dentil blocks along the cornice
    for dx in [i * 0.42 for i in range(-6, 7)]:
        make_box(f"Dentil_{dx:.2f}", (dx, 0.28, 4.28), (0.16, 0.14, 0.10), mat_cream)
        
    # Upper Parapet Wall
    make_box("Parapet_Wall", (0, -1.75, 4.75), (5.6, 3.5, 0.60), mat_mint)
    make_box("Parapet_TopTrim", (0, 0.05, 5.08), (5.8, 0.42, 0.12), mat_cream)
    
    # Center decorative pediment / arch above roofline
    make_cylinder("Parapet_CenterArch", (0, 0.04, 5.08), r=0.92, h=0.25, segs=28, mat=mat_mint, rot=(math.radians(90), 0, 0))
    make_cylinder("Parapet_ArchRim", (0, 0.07, 5.08), r=0.98, h=0.22, segs=28, mat=mat_cream, rot=(math.radians(90), 0, 0))
    # Golden finial orb on top center
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(0, 0.06, 6.15))
    orb = bpy.context.active_object
    orb.name = "Roof_FinialOrb"
    orb.data.materials.append(mat_gold_text)
    link_obj(orb)

    # Stylized chimney on left roof
    make_box("Chimney_Body", (-2.1, -1.2, 5.5), (0.6, 0.6, 1.2), mat_cream)
    make_box("Chimney_Cap", (-2.1, -1.2, 6.16), (0.75, 0.75, 0.12), mat_awning_coral)
    make_cylinder("Chimney_Pot", (-2.1, -1.2, 6.38), r=0.18, h=0.35, segs=12, mat=mat_awning_coral)

    # ---------------------------------------------------------
    # 5. Storefront Facade (Charming Door & Large Display Windows)
    # ---------------------------------------------------------
    # Entrance Doorway (Centered at X = 0)
    # Placed at Y = 0.05 so it's fully visible and proud of the main wall
    # Door Outer Surround (Cream)
    make_box("Door_Surround_L", (-0.72, 0.05, 1.35), (0.12, 0.16, 2.3), mat_cream)
    make_box("Door_Surround_R", (0.72, 0.05, 1.35), (0.12, 0.16, 2.3), mat_cream)
    make_box("Door_Surround_Top", (0, 0.05, 2.50), (1.56, 0.16, 0.12), mat_cream)
    # Decorative pediment over the door
    make_box("Door_Pediment", (0, 0.08, 2.62), (1.68, 0.20, 0.12), mat_dark_pink)
    
    # Door Step
    make_box("Entrance_Step", (0, 0.22, 0.25), (1.65, 0.35, 0.10), mat_cream)
    
    # Door Body (Pastel Strawberry Pink)
    make_box("Door_Body", (0, 0.04, 1.30), (1.30, 0.08, 2.20), mat_pink)
    # Door lower panel detail (beveled border)
    make_box("Door_Lower_Panel", (0, 0.09, 0.65), (0.96, 0.04, 0.72), mat_dark_pink)
    make_box("Door_Lower_Panel_Inner", (0, 0.115, 0.65), (0.84, 0.02, 0.60), mat_pink)
    
    # Door upper window (warm glass letting light shine through)
    make_box("Door_Upper_Window", (0, 0.08, 1.70), (0.96, 0.04, 0.96), mat_glass)
    make_box("Door_Window_MullionH", (0, 0.11, 1.70), (0.96, 0.03, 0.05), mat_cream)
    make_box("Door_Window_MullionV", (0, 0.11, 1.70), (0.05, 0.03, 0.96), mat_cream)
    
    # Brass Handle & Kickplate
    make_cylinder("Door_Handle", (0.48, 0.13, 1.25), r=0.035, h=0.22, segs=8, mat=mat_brass, rot=(math.radians(90), 0, 0))
    make_box("Door_Kickplate", (0, 0.09, 0.27), (1.15, 0.03, 0.12), mat_brass)
    
    # Welcome Doormat
    make_box("DoorMat", (0, 0.46, 0.21), (1.20, 0.55, 0.02), mat_coir)
    make_box("DoorMat_Border", (0, 0.46, 0.215), (1.28, 0.63, 0.015), mat_wood_sign)

    # Large Display Windows (Left & Right)
    for side, x_center in [("Left", -1.75), ("Right", 1.75)]:
        # Window Sill
        make_box(f"Window_Sill_{side}", (x_center, 0.12, 0.70), (1.80, 0.30, 0.12), mat_cream)
        # Window Outer Frame
        make_box(f"Window_Frame_Bottom_{side}", (x_center, 0.05, 0.78), (1.70, 0.14, 0.08), mat_cream)
        make_box(f"Window_Frame_Top_{side}", (x_center, 0.05, 2.50), (1.70, 0.14, 0.08), mat_cream)
        make_box(f"Window_Frame_L_{side}", (x_center - 0.81, 0.05, 1.64), (0.08, 0.14, 1.70), mat_cream)
        make_box(f"Window_Frame_R_{side}", (x_center + 0.81, 0.05, 1.64), (0.08, 0.14, 1.70), mat_cream)
        
        # Grid Mullions (Classic bakery 6-pane grid)
        make_box(f"Window_Mullion_V_{side}", (x_center, 0.06, 1.64), (0.05, 0.10, 1.68), mat_cream)
        make_box(f"Window_Mullion_H1_{side}", (x_center, 0.06, 1.25), (1.60, 0.10, 0.05), mat_cream)
        make_box(f"Window_Mullion_H2_{side}", (x_center, 0.06, 1.95), (1.60, 0.10, 0.05), mat_cream)
        
        # Transparent Glass Pane
        make_box(f"Window_Glass_{side}", (x_center, 0.04, 1.64), (1.60, 0.02, 1.68), mat_glass)

        # Interior Bakery Display Counter (Visible through window)
        make_box(f"Bakery_Counter_{side}", (x_center, -0.40, 0.60), (1.50, 0.6, 0.75), mat_cream)
        make_box(f"Bakery_ShelfTop_{side}", (x_center, -0.38, 1.00), (1.54, 0.62, 0.05), mat_wood_sign)
        
        # Tiered cake stands with mini cookies
        for tier_x in [-0.42, 0.42]:
            # Stand
            make_cylinder(f"Stand_Base_{side}_{tier_x}", (x_center + tier_x, -0.35, 1.05), r=0.16, h=0.04, segs=12, mat=mat_cream)
            make_cylinder(f"Stand_Stem_{side}_{tier_x}", (x_center + tier_x, -0.35, 1.15), r=0.035, h=0.18, segs=8, mat=mat_cream)
            make_cylinder(f"Stand_Plate_{side}_{tier_x}", (x_center + tier_x, -0.35, 1.25), r=0.28, h=0.025, segs=16, mat=mat_cream)
            
            # Mini cookies on plate!
            cookie_mat = mat_dough if tier_x < 0 else mat_frosting
            for angle in [0, 72, 144, 216, 288]:
                rad = math.radians(angle)
                cx = x_center + tier_x + 0.14 * math.cos(rad)
                cy = -0.35 + 0.14 * math.sin(rad)
                make_cylinder(f"MiniCookie_{side}_{tier_x}_{angle}", (cx, cy, 1.28), r=0.05, h=0.02, segs=8, mat=cookie_mat)
                make_cylinder(f"MiniChip_{side}_{tier_x}_{angle}", (cx, cy, 1.295), r=0.018, h=0.012, segs=5, mat=mat_choc)

    # ---------------------------------------------------------
    # 6. Striped Awning
    # ---------------------------------------------------------
    awning_width = 5.2
    awning_num_stripes = 14
    stripe_w = awning_width / awning_num_stripes
    
    # Awning sloped stripes
    for i in range(awning_num_stripes):
        sx = -awning_width/2 + (i + 0.5) * stripe_w
        s_mat = mat_awning_coral if i % 2 == 0 else mat_awning_cream
        
        # Slanted canopy stripe
        angle_rad = math.radians(26)
        canopy_stripe = make_box(f"AwningStripe_{i}", (sx, 0.65, 2.58), (stripe_w * 0.98, 1.34, 0.04), mat=s_mat)
        canopy_stripe.rotation_euler = (angle_rad, 0, 0)
        
        # Front hanging valance
        make_box(f"Valance_{i}", (sx, 1.26, 2.08), (stripe_w * 0.98, 0.03, 0.26), mat=s_mat)
        # Scallop rounded bottom
        make_cylinder(f"Scallop_{i}", (sx, 1.26, 1.95), r=stripe_w*0.48, h=0.035, segs=12, mat=s_mat, rot=(math.radians(90), 0, 0))

    # Awning Support Struts & Beam (Dark Iron)
    make_box("Awning_FrontBar", (0, 1.26, 2.22), (awning_width + 0.12, 0.06, 0.06), mat_dark_iron)
    for strut_x in [-2.5, 2.5]:
        make_cylinder(f"Awning_Strut_{strut_x}", (strut_x, 0.65, 2.05), r=0.03, h=1.5, segs=8, mat=mat_dark_iron, rot=(math.radians(52), 0, 0))

    # ---------------------------------------------------------
    # 7. Storefront Sign ("Cookie Shop")
    # ---------------------------------------------------------
    sign_z = 3.32
    # Rich dark wood signboard with gold and cream trim
    make_box("Sign_Board_Backing", (0, 0.16, sign_z), (2.95, 0.08, 0.70), mat_wood_sign)
    make_box("Sign_Board_Inner", (0, 0.20, sign_z), (2.80, 0.03, 0.56), mat_wood_sign)
    make_box("Sign_Board_Frame_Top", (0, 0.21, sign_z + 0.32), (3.0, 0.08, 0.06), mat_cream)
    make_box("Sign_Board_Frame_Bottom", (0, 0.21, sign_z - 0.32), (3.0, 0.08, 0.06), mat_cream)
    make_box("Sign_Board_Frame_L", (-1.47, 0.21, sign_z), (0.06, 0.08, 0.70), mat_cream)
    make_box("Sign_Board_Frame_R", (1.47, 0.21, sign_z), (0.06, 0.08, 0.70), mat_cream)
    
    # 3D Text: "Cookie Shop"
    # Facing towards +Y (front face towards camera at +Y), upright along +Z
    bpy.ops.object.text_add(location=(0, 0.24, sign_z - 0.12), rotation=(math.radians(90), 0, math.radians(180)))
    txt_obj = bpy.context.active_object
    txt_obj.name = "Text_CookieShop"
    txt_obj.data.body = "Cookie Shop"
    txt_obj.data.align_x = 'CENTER'
    txt_obj.data.align_y = 'CENTER'
    txt_obj.data.size = 0.36
    txt_obj.data.extrude = 0.045
    txt_obj.data.bevel_depth = 0.015
    txt_obj.data.bevel_resolution = 2
    # Flip scale X so letters read left-to-right correctly from +Y
    txt_obj.scale = (-1, 1, 1)
    txt_obj.data.materials.append(mat_gold_text)
    link_obj(txt_obj)
    
    # Decorative mini cookie icons flanking the text
    for icon_x in [-1.18, 1.18]:
        make_cylinder(f"Sign_CookieIcon_{icon_x}", (icon_x, 0.23, sign_z), r=0.15, h=0.03, segs=12, mat=mat_dough, rot=(math.radians(90), 0, 0))
        for chip_i, (cx_off, cz_off) in enumerate([(-0.04, 0.04), (0.05, 0.03), (0.0, -0.05)]):
            make_cylinder(f"Sign_IconChip_{icon_x}_{chip_i}", (icon_x + cx_off, 0.25, sign_z + cz_off), r=0.03, h=0.02, segs=6, mat=mat_choc, rot=(math.radians(90), 0, 0))

    # Gooseneck Lamps over the sign
    for lamp_x in [-0.9, 0.9]:
        make_cylinder(f"Gooseneck_Plate_{lamp_x}", (lamp_x, 0.08, sign_z + 0.48), r=0.07, h=0.03, segs=8, mat=mat_brass, rot=(math.radians(90), 0, 0))
        make_box(f"Gooseneck_Arm_{lamp_x}", (lamp_x, 0.26, sign_z + 0.52), (0.03, 0.36, 0.03), mat_brass)
        
        # Shade
        bpy.ops.mesh.primitive_cone_add(radius1=0.13, radius2=0.04, depth=0.12, location=(lamp_x, 0.42, sign_z + 0.46), rotation=(0, 0, 0))
        shade = bpy.context.active_object
        shade.name = f"Gooseneck_Shade_{lamp_x}"
        shade.data.materials.append(mat_brass)
        link_obj(shade)
        
        # Glowing bulb
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(lamp_x, 0.42, sign_z + 0.40))
        bulb = bpy.context.active_object
        bulb.name = f"Gooseneck_Bulb_{lamp_x}"
        bulb.data.materials.append(mat_glow)
        link_obj(bulb)
        
        # Spot light pointing at sign
        light_data = bpy.data.lights.new(name=f"Light_SignLamp_{lamp_x}", type='SPOT')
        light_data.energy = 35.0
        light_data.color = (1.0, 0.88, 0.65)
        light_data.spot_size = math.radians(60)
        light_data.spot_blend = 0.3
        lamp_obj = bpy.data.objects.new(name=f"Light_SignLamp_{lamp_x}", object_data=light_data)
        lamp_obj.location = (lamp_x, 0.42, sign_z + 0.38)
        lamp_obj.rotation_euler = (math.radians(-45), 0, 0)
        link_obj(lamp_obj)

    # ---------------------------------------------------------
    # 8. Giant Chocolate Chip Cookie above the Entrance
    # ---------------------------------------------------------
    cookie_z = 4.38
    cookie_r = 0.74
    cookie_thick = 0.25
    
    # Giant Cookie Dough Base (Tilted slightly forward towards the street)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=cookie_r, depth=cookie_thick, location=(0, 0.32, cookie_z), rotation=(math.radians(94), 0, 0))
    giant_cookie = bpy.context.active_object
    giant_cookie.name = "Giant_Cookie_Dough"
    giant_cookie.data.materials.append(mat_dough)
    link_obj(giant_cookie)
    
    # Soft bevel for baked cookie edge
    bev = giant_cookie.modifiers.new(name="CookieBevel", type='BEVEL')
    bev.width = 0.07
    bev.segments = 2
    
    # Wall brackets holding the giant cookie
    for bx in [-0.5, 0.5]:
        make_box(f"Cookie_Bracket_{bx}", (bx, 0.16, cookie_z - 0.2), (0.05, 0.30, 0.5), mat_dark_iron)
        make_cylinder(f"Cookie_Scroll_{bx}", (bx, 0.24, cookie_z - 0.45), r=0.12, h=0.04, segs=12, mat=mat_dark_iron, rot=(0, math.radians(90), 0))

    # Chunky Dark Chocolate Chips embedded in the giant cookie
    chip_data = [
        (0.0, 0.05, 0.13, 15),
        (-0.35, 0.28, 0.12, 40),
        (0.38, 0.24, 0.13, -25),
        (-0.25, -0.22, 0.14, 60),
        (0.32, -0.25, 0.12, 10),
        (0.04, 0.42, 0.11, -45),
        (-0.48, -0.02, 0.12, 30),
        (0.50, 0.02, 0.13, -70),
        (-0.16, 0.20, 0.10, 120),
        (0.18, -0.08, 0.11, 85),
        (-0.10, -0.45, 0.10, -15),
        (0.12, 0.48, 0.09, 50),
    ]
    for idx, (cx, cz, cr, crot) in enumerate(chip_data):
        cy = 0.32 + cookie_thick/2 + 0.02
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=cr, radius2=cr*0.35, depth=cr*1.2, location=(cx, cy, cookie_z + cz), rotation=(math.radians(94), 0, math.radians(crot)))
        chip = bpy.context.active_object
        chip.name = f"Giant_ChocChip_{idx}"
        chip.data.materials.append(mat_choc)
        link_obj(chip)

    # ---------------------------------------------------------
    # 9. Sidewalk Dressing & Props
    # ---------------------------------------------------------
    # Window Flower Boxes (under Left & Right windows)
    for side, x_center in [("Left", -1.75), ("Right", 1.75)]:
        make_box(f"FlowerBox_Trough_{side}", (x_center, 0.28, 0.60), (1.68, 0.24, 0.18), mat_cream)
        make_box(f"FlowerBox_Trim_{side}", (x_center, 0.29, 0.68), (1.72, 0.26, 0.04), mat_awning_coral)
        
        for fi, fx in enumerate([-0.6, -0.3, 0.0, 0.3, 0.6]):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.14, location=(x_center + fx, 0.28, 0.74))
            bush = bpy.context.active_object
            bush.name = f"Bush_{side}_{fi}"
            bush.data.materials.append(mat_leaf)
            link_obj(bush)
            
            f_mat = mat_flower_pink if fi % 2 == 0 else mat_flower_yellow
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(x_center + fx, 0.30, 0.86))
            flower = bpy.context.active_object
            flower.name = f"Flower_{side}_{fi}"
            flower.data.materials.append(f_mat)
            link_obj(flower)

    # A-Frame Sidewalk Chalkboard Menu Sign
    af_x, af_y = 1.35, 1.45
    make_box("Chalk_Leg_F", (af_x, af_y - 0.08, 0.58), (0.55, 0.04, 0.78), mat_wood_sign).rotation_euler = (math.radians(-12), 0, math.radians(15))
    make_box("Chalk_Leg_B", (af_x, af_y + 0.08, 0.58), (0.55, 0.04, 0.78), mat_wood_sign).rotation_euler = (math.radians(12), 0, math.radians(15))
    chalk_face = make_box("Chalk_Face", (af_x, af_y - 0.10, 0.60), (0.45, 0.02, 0.60), mat_chalkboard)
    chalk_face.rotation_euler = (math.radians(-12), 0, math.radians(15))
    # Chalk doodle
    make_cylinder("Chalk_Cookie_Doodle", (af_x - 0.02, af_y - 0.12, 0.72), r=0.08, h=0.02, segs=10, mat=mat_cream, rot=(math.radians(78), 0, math.radians(15)))
    for li, lz in enumerate([0.55, 0.48, 0.42]):
        c_line = make_box(f"Chalk_Line_{li}", (af_x - 0.01, af_y - 0.12, lz), (0.30 - li*0.06, 0.015, 0.02), mat_cream)
        c_line.rotation_euler = (math.radians(-12), 0, math.radians(15))

    # Vintage Street Lamppost on the sidewalk curb (Left)
    lp_x, lp_y = -3.2, 2.2
    make_box("Lamp_Plinth", (lp_x, lp_y, 0.30), (0.42, 0.42, 0.22), mat_dark_iron)
    make_cylinder("Lamp_BaseRing", (lp_x, lp_y, 0.45), r=0.18, h=0.15, segs=12, mat=mat_dark_iron)
    make_cylinder("Lamp_Pole", (lp_x, lp_y, 1.8), r=0.07, h=2.6, segs=10, mat=mat_dark_iron)
    make_box("Lamp_Bracket", (lp_x + 0.22, lp_y, 3.1), (0.45, 0.08, 0.08), mat_dark_iron)
    make_cylinder("Lamp_LanternCap", (lp_x + 0.42, lp_y, 3.25), r=0.22, h=0.10, segs=6, mat=mat_dark_iron)
    make_cylinder("Lamp_LanternGlass", (lp_x + 0.42, lp_y, 3.0), r=0.16, h=0.36, segs=6, mat=mat_glow)
    make_cylinder("Lamp_LanternBase", (lp_x + 0.42, lp_y, 2.8), r=0.14, h=0.06, segs=6, mat=mat_dark_iron)
    
    # Lamppost warm light
    lamp_lt = bpy.data.lights.new(name="Light_StreetLamp", type='POINT')
    lamp_lt.energy = 55.0
    lamp_lt.color = (1.0, 0.82, 0.50)
    lamp_lt.shadow_soft_size = 0.25
    lamp_lt_obj = bpy.data.objects.new(name="Light_StreetLamp", object_data=lamp_lt)
    lamp_lt_obj.location = (lp_x + 0.42, lp_y, 2.98)
    link_obj(lamp_lt_obj)

    # Outdoor Café Bistro Table & Stools (Right)
    bt_x, bt_y = 2.4, 1.85
    make_cylinder("Bistro_Table_Top", (bt_x, bt_y, 0.72), r=0.48, h=0.04, segs=18, mat=mat_pink)
    make_cylinder("Bistro_Table_Rim", (bt_x, bt_y, 0.71), r=0.50, h=0.02, segs=18, mat=mat_cream)
    make_cylinder("Bistro_Table_Leg", (bt_x, bt_y, 0.45), r=0.04, h=0.55, segs=8, mat=mat_dark_iron)
    make_cylinder("Bistro_Table_Base", (bt_x, bt_y, 0.22), r=0.26, h=0.04, segs=12, mat=mat_dark_iron)
    
    for si, (st_x, st_y) in enumerate([(-0.45, 0.0), (0.45, 0.0)]):
        make_cylinder(f"Bistro_Stool_Seat_{si}", (bt_x + st_x, bt_y + st_y, 0.48), r=0.22, h=0.04, segs=16, mat=mat_awning_coral)
        make_cylinder(f"Bistro_Stool_Leg_{si}", (bt_x + st_x, bt_y + st_y, 0.32), r=0.03, h=0.32, segs=8, mat=mat_dark_iron)
        make_cylinder(f"Bistro_Stool_Base_{si}", (bt_x + st_x, bt_y + st_y, 0.21), r=0.15, h=0.03, segs=10, mat=mat_dark_iron)
        
    # Cookie & cup on the table
    make_cylinder("Table_Plate", (bt_x - 0.12, bt_y + 0.08, 0.75), r=0.14, h=0.015, segs=16, mat=mat_cream)
    make_cylinder("Table_Cookie", (bt_x - 0.12, bt_y + 0.08, 0.77), r=0.08, h=0.02, segs=12, mat=mat_dough)
    make_cylinder("Table_Cookie_Chip1", (bt_x - 0.14, bt_y + 0.09, 0.785), r=0.025, h=0.012, segs=6, mat=mat_choc)
    make_cylinder("Table_Cookie_Chip2", (bt_x - 0.10, bt_y + 0.06, 0.785), r=0.02, h=0.012, segs=6, mat=mat_choc)
    make_cylinder("Table_Saucer", (bt_x + 0.15, bt_y - 0.06, 0.75), r=0.11, h=0.015, segs=14, mat=mat_cream)
    make_cylinder("Table_Cup", (bt_x + 0.15, bt_y - 0.06, 0.81), r=0.07, h=0.10, segs=14, mat=mat_pink)
    make_cylinder("Table_Coffee", (bt_x + 0.15, bt_y - 0.06, 0.84), r=0.06, h=0.02, segs=12, mat=mat_wood_sign)

    # ---------------------------------------------------------
    # 10. Warm, Inviting Lighting Setup
    # ---------------------------------------------------------
    # Warm Golden Hour Sunlight
    sun_data = bpy.data.lights.new(name="Light_SunKey", type='SUN')
    sun_data.energy = 2.0
    sun_data.color = (1.0, 0.92, 0.82)
    sun_data.angle = math.radians(14)
    sun_obj = bpy.data.objects.new(name="Light_SunKey", object_data=sun_data)
    sun_obj.location = (6.0, 8.0, 10.0)
    sun_obj.rotation_euler = (math.radians(-42), math.radians(24), math.radians(-35))
    link_obj(sun_obj)

    # Soft Ambient Sky Fill Light
    sky_data = bpy.data.lights.new(name="Light_SkyFill", type='SUN')
    sky_data.energy = 0.5
    sky_data.color = (0.75, 0.85, 1.0)
    sky_obj = bpy.data.objects.new(name="Light_SkyFill", object_data=sky_data)
    sky_obj.location = (-6.0, 4.0, 8.0)
    sky_obj.rotation_euler = (math.radians(-50), math.radians(-30), math.radians(120))
    link_obj(sky_obj)

    # Interior Warm Cozy Lights (behind windows)
    for side, x_pos in [("Left", -1.75), ("Right", 1.75)]:
        in_lt = bpy.data.lights.new(name=f"Light_Interior_{side}", type='POINT')
        in_lt.energy = 120.0
        in_lt.color = (1.0, 0.80, 0.48)
        in_lt.shadow_soft_size = 0.35
        in_obj = bpy.data.objects.new(name=f"Light_Interior_{side}", object_data=in_lt)
        in_obj.location = (x_pos, -0.4, 1.8)
        link_obj(in_obj)

    # Door entrance lantern
    door_lt = bpy.data.lights.new(name="Light_Entrance_Lantern", type='POINT')
    door_lt.energy = 70.0
    door_lt.color = (1.0, 0.84, 0.55)
    door_lt.shadow_soft_size = 0.25
    door_obj = bpy.data.objects.new(name="Light_Entrance_Lantern", object_data=door_lt)
    door_obj.location = (0.0, 0.25, 2.7)
    link_obj(door_obj)

    # ---------------------------------------------------------
    # 11. Camera Setup (Showing the entire storefront)
    # ---------------------------------------------------------
    cam_data = bpy.data.cameras.new(name="Storefront_Camera")
    cam_data.lens = 35.0  # Slightly wider lens to capture the full diorama
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new(name="Storefront_Camera", object_data=cam_data)
    
    # Position camera back and high for a gorgeous 3/4 storefront view
    cam_obj.location = (2.2, 9.6, 4.2)
    target = Vector((0.0, 0.8, 2.5))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    
    link_obj(cam_obj)
    scene.camera = cam_obj

    # ---------------------------------------------------------
    # 12. World Background & Render Settings
    # ---------------------------------------------------------
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("CookieShop_World")
        scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        # Soft pleasant pastel sky blue/peach gradient
        bg_node.inputs['Color'].default_value = (0.75, 0.84, 0.92, 1.0)
        bg_node.inputs['Strength'].default_value = 0.65

    # Render settings
    render = scene.render
    available_engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    if 'BLENDER_EEVEE' in available_engines:
        render.engine = 'BLENDER_EEVEE'
    elif 'BLENDER_EEVEE_NEXT' in available_engines:
        render.engine = 'BLENDER_EEVEE_NEXT'

    render.resolution_x = 1280
    render.resolution_y = 960
    render.resolution_percentage = 100
    render.image_settings.file_format = 'PNG'
    
    if hasattr(scene, 'view_settings'):
        scene.view_settings.view_transform = 'AgX' if 'AgX' in [v.identifier for v in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Standard'
        scene.view_settings.look = 'Medium High Contrast' if 'Medium High Contrast' in [l.identifier for l in bpy.types.ColorManagedViewSettings.bl_rna.properties['look'].enum_items] else 'None'

    print("Refined Cookie Shop successfully created!")
    return "Refined Cookie Shop completed."

create_cookie_shop()
