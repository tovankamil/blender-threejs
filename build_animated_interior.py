"""
build_animated_interior.py
Creates a complete, animated low-poly interior for the Cookie Shop in Blender 5.3:
- Preserves all existing exterior, sidewalk, table, chairs, moon, and stars.
- Adds Floor & Walls with wood planks, pastel mint paneling, peach wallpaper, white moldings.
- Adds Front Counter with illuminated glass display case full of pastries, cookies, and POS cashier.
- Adds Baking Area with glowing oven (#FF6600), rolling cooling rack with cookie trays, flour sacks.
- Adds 3 warm hanging pendant lights with EEVEE point lights.
- Adds Cute Baker Character (Pelayan) with toque, apron, rig, and 240-frame looping animation.
- Adds "Camera_Interior" (22mm wide angle, eye level ~1.5m).
- Sets up renders and saves cookie_shop_animated_interior.blend.
"""

import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Euler, Matrix

def run_build():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.frame_start = 1
    scene.frame_end = 240
    scene.render.fps = 24

    # -------------------------------------------------------------------------
    # 1. Collection Setup
    # -------------------------------------------------------------------------
    col_name = "Cookie_Shop_Interior"
    interior_col = bpy.data.collections.get(col_name)
    if not interior_col:
        interior_col = bpy.data.collections.new(col_name)
        scene.collection.children.link(interior_col)

    def link_obj(obj):
        # Ensure obj is linked to interior_col and unlinked from root if needed
        if obj.name not in interior_col.objects:
            interior_col.objects.link(obj)
        if obj.name in scene.collection.objects:
            scene.collection.objects.unlink(obj)

    # -------------------------------------------------------------------------
    # 2. Material Helper
    # -------------------------------------------------------------------------
    def get_or_create_mat(name, base_color, roughness=0.6, metallic=0.0,
                           emission_color=None, emission_strength=0.0,
                           transmission=0.0, alpha=1.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out_node = nodes.new(type='ShaderNodeOutputMaterial')
        out_node.location = (300, 0)
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

        # Set BSDF parameters
        if isinstance(base_color, str):
            # hex to rgba
            hex_c = base_color.lstrip('#')
            r = int(hex_c[0:2], 16) / 255.0
            g = int(hex_c[2:4], 16) / 255.0
            b = int(hex_c[4:6], 16) / 255.0
            color = (r, g, b, alpha)
        else:
            color = base_color

        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic

        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = transmission

        if emission_color and emission_strength > 0:
            if isinstance(emission_color, str):
                hex_c = emission_color.lstrip('#')
                er = int(hex_c[0:2], 16) / 255.0
                eg = int(hex_c[2:4], 16) / 255.0
                eb = int(hex_c[4:6], 16) / 255.0
                e_col = (er, eg, eb, 1.0)
            else:
                e_col = emission_color
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = e_col
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = e_col
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emission_strength

        if alpha < 1.0 or transmission > 0.5:
            mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else 'HASHED'

        return mat

    # Define palette materials
    mat_wood_floor = get_or_create_mat("Mat_Int_WoodFloor", "#8B5A2B", roughness=0.55)
    mat_wood_plank2 = get_or_create_mat("Mat_Int_WoodFloor2", "#7E5124", roughness=0.55)
    mat_mint_panel  = get_or_create_mat("Mat_Int_MintPanel", "#A2D5C6", roughness=0.6)
    mat_peach_wall  = get_or_create_mat("Mat_Int_PeachWall", "#F8C5A8", roughness=0.6)
    mat_white_trim  = get_or_create_mat("Mat_Int_WhiteTrim", "#FDFBF7", roughness=0.45)
    mat_counter_oak = get_or_create_mat("Mat_Int_CounterOak", "#C88A4B", roughness=0.45)
    mat_counter_base= get_or_create_mat("Mat_Int_CounterBase", "#F5ECE1", roughness=0.5)
    mat_disp_glass  = get_or_create_mat("Mat_Int_DisplayGlass", "#FFFFFF", roughness=0.05, transmission=0.92, alpha=0.35)
    mat_disp_glow   = get_or_create_mat("Mat_Int_DisplayGlow", "#FFE6A3", roughness=0.2, emission_color="#FFE6A3", emission_strength=4.5)
    mat_oven_metal  = get_or_create_mat("Mat_Int_OvenMetal", "#33383E", roughness=0.4, metallic=0.7)
    mat_oven_glow   = get_or_create_mat("Mat_Int_OvenGlow", "#FF6600", roughness=0.2, emission_color="#FF6600", emission_strength=9.0)
    mat_chalkboard  = get_or_create_mat("Mat_Int_Chalkboard", "#1E2328", roughness=0.85)
    mat_chalk_txt   = get_or_create_mat("Mat_Int_ChalkText", "#FFFFFF", roughness=0.3, emission_color="#FFFFFF", emission_strength=1.2)
    mat_cookie_gold = get_or_create_mat("Mat_Int_CookieGold", "#D49B6A", roughness=0.7)
    mat_cookie_choc = get_or_create_mat("Mat_Int_CookieChoc", "#382012", roughness=0.65)
    mat_pastry_pink = get_or_create_mat("Mat_Int_PastryPink", "#FF8BA7", roughness=0.4)
    mat_pastry_crois= get_or_create_mat("Mat_Int_PastryCroissant", "#E5A952", roughness=0.6)
    mat_baker_skin  = get_or_create_mat("Mat_Int_BakerSkin", "#FFD8C2", roughness=0.7)
    mat_baker_apron = get_or_create_mat("Mat_Int_BakerApron", "#F4B2B2", roughness=0.6)
    mat_baker_shirt = get_or_create_mat("Mat_Int_BakerShirt", "#F5F5F5", roughness=0.5)
    mat_baker_hat   = get_or_create_mat("Mat_Int_BakerHat", "#FFFFFF", roughness=0.4)
    mat_baker_pants = get_or_create_mat("Mat_Int_BakerPants", "#2A3644", roughness=0.7)
    mat_baker_shoes = get_or_create_mat("Mat_Int_BakerShoes", "#4E3120", roughness=0.5)
    mat_brass       = get_or_create_mat("Mat_Int_Brass", "#D4AF37", roughness=0.3, metallic=0.85)
    mat_pendant_glow= get_or_create_mat("Mat_Int_PendantGlow", "#FFB366", roughness=0.2, emission_color="#FFB366", emission_strength=5.0)
    mat_flour_sack  = get_or_create_mat("Mat_Int_FlourSack", "#E6DCB8", roughness=0.8)

    # -------------------------------------------------------------------------
    # Helper: Box Creation
    # -------------------------------------------------------------------------
    def create_box(name, loc, size, mat=None):
        existing = bpy.data.objects.get(name)
        if existing:
            bpy.data.objects.remove(existing, do_unlink=True)

        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        link_obj(obj)

        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= size[0]
            v.co.y *= size[1]
            v.co.z *= size[2]
        bm.to_mesh(mesh)
        bm.free()

        obj.location = loc
        if mat:
            obj.data.materials.append(mat)
        return obj

    def create_cylinder(name, loc, radius, depth, mat=None, segments=16):
        existing = bpy.data.objects.get(name)
        if existing:
            bpy.data.objects.remove(existing, do_unlink=True)

        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        link_obj(obj)

        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                              radius1=radius, radius2=radius, depth=depth)
        bm.to_mesh(mesh)
        bm.free()

        obj.location = loc
        if mat:
            obj.data.materials.append(mat)
        return obj

    # -------------------------------------------------------------------------
    # 3. Ensure Windows Visibility
    # -------------------------------------------------------------------------
    # Hide the old solid opaque glow planes that blocked view into the shop
    for side in ["Left", "Right"]:
        gp = bpy.data.objects.get(f"Interior_GlowPlane_{side}")
        if gp:
            gp.hide_render = True
            gp.hide_viewport = True

    # -------------------------------------------------------------------------
    # 4. Interior Architecture (Floor, Walls, Trim, Ceiling)
    # -------------------------------------------------------------------------
    # Floor: X in [-2.85, 2.85], Y in [-3.25, -0.05], Z = 0.20
    floor_base = create_box("Int_Floor_Base", (0.0, -1.65, 0.20), (5.70, 3.20, 0.04), mat_wood_floor)

    # Decorative wooden planks across floor for charming low-poly floorboards
    num_planks = 12
    plank_width = 3.20 / num_planks
    for i in range(num_planks):
        py = -3.25 + (i + 0.5) * plank_width
        p_mat = mat_wood_floor if (i % 2 == 0) else mat_wood_plank2
        create_box(f"Int_Floor_Plank_{i}", (0.0, py, 0.222), (5.68, plank_width * 0.94, 0.008), p_mat)

    # Back Wall: at Y = -3.25, Z from 0.20 to 3.05
    # Lower Mint Wainscoting (Z = 0.20 to 1.25)
    create_box("Int_BackWall_Lower", (0.0, -3.24, 0.725), (5.70, 0.04, 1.05), mat_mint_panel)
    # White Chair Rail Molding
    create_box("Int_BackWall_ChairRail", (0.0, -3.22, 1.25), (5.70, 0.06, 0.06), mat_white_trim)
    # Upper Peach Wall (Z = 1.25 to 3.05)
    create_box("Int_BackWall_Upper", (0.0, -3.24, 2.15), (5.70, 0.04, 1.74), mat_peach_wall)
    # White Crown Molding along top
    create_box("Int_BackWall_Crown", (0.0, -3.21, 3.01), (5.70, 0.08, 0.08), mat_white_trim)
    # Baseboard
    create_box("Int_BackWall_Baseboard", (0.0, -3.22, 0.26), (5.70, 0.05, 0.10), mat_white_trim)

    # Left Wall: at X = -2.85, Y in [-3.25, -0.05]
    create_box("Int_LeftWall_Lower", (-2.84, -1.65, 0.725), (0.04, 3.20, 1.05), mat_mint_panel)
    create_box("Int_LeftWall_ChairRail", (-2.82, -1.65, 1.25), (0.06, 3.20, 0.06), mat_white_trim)
    create_box("Int_LeftWall_Upper", (-2.84, -1.65, 2.15), (0.04, 3.20, 1.74), mat_peach_wall)
    create_box("Int_LeftWall_Crown", (-2.81, -1.65, 3.01), (0.08, 3.20, 0.08), mat_white_trim)
    create_box("Int_LeftWall_Baseboard", (-2.82, -1.65, 0.26), (0.05, 3.20, 0.10), mat_white_trim)

    # Right Wall: at X = +2.85, Y in [-3.25, -0.05]
    create_box("Int_RightWall_Lower", (2.84, -1.65, 0.725), (0.04, 3.20, 1.05), mat_mint_panel)
    create_box("Int_RightWall_ChairRail", (2.82, -1.65, 1.25), (0.06, 3.20, 0.06), mat_white_trim)
    create_box("Int_RightWall_Upper", (2.84, -1.65, 2.15), (0.04, 3.20, 1.74), mat_peach_wall)
    create_box("Int_RightWall_Crown", (2.81, -1.65, 3.01), (0.08, 3.20, 0.08), mat_white_trim)
    create_box("Int_RightWall_Baseboard", (2.82, -1.65, 0.26), (0.05, 3.20, 0.10), mat_white_trim)

    # Ceiling: at Z = 3.05
    create_box("Int_Ceiling", (0.0, -1.65, 3.06), (5.70, 3.20, 0.04), mat_white_trim)

    # -------------------------------------------------------------------------
    # 5. Front Counter & Bakery Display Case
    # -------------------------------------------------------------------------
    # Main counter sits at Y = -1.45, facing +Y (towards entrance)
    # Left Section: Glass Display Case (X from -2.35 to -0.45, width = 1.90, depth = 0.65, height = 0.95)
    # Base cabinet
    create_box("Int_Disp_Base", (-1.40, -1.45, 0.38), (1.90, 0.65, 0.34), mat_counter_base)
    create_box("Int_Disp_Trim_Lower", (-1.40, -1.45, 0.54), (1.94, 0.68, 0.04), mat_white_trim)

    # Glass display hood
    create_box("Int_Disp_Glass_Front", (-1.40, -1.13, 0.85), (1.88, 0.02, 0.58), mat_disp_glass)
    create_box("Int_Disp_Glass_Top",   (-1.40, -1.45, 1.13), (1.88, 0.62, 0.02), mat_disp_glass)
    create_box("Int_Disp_Glass_Left",  (-2.33, -1.45, 0.85), (0.02, 0.62, 0.58), mat_disp_glass)
    create_box("Int_Disp_Glass_Right", (-0.47, -1.45, 0.85), (0.02, 0.62, 0.58), mat_disp_glass)

    # Wooden corner corner-pillars for stylized bakery charm
    for px in [-2.34, -0.46]:
        for py in [-1.75, -1.14]:
            create_box(f"Int_Disp_Pillar_{px}_{py}", (px, py, 0.85), (0.04, 0.04, 0.58), mat_counter_oak)

    # Internal Tiered Glass Shelves
    create_box("Int_Disp_Shelf_Bottom", (-1.40, -1.44, 0.68), (1.82, 0.55, 0.02), mat_disp_glass)
    create_box("Int_Disp_Shelf_Middle", (-1.40, -1.44, 0.90), (1.82, 0.52, 0.02), mat_disp_glass)

    # Internal warm LED emission strip
    create_box("Int_Disp_LED_Strip", (-1.40, -1.16, 1.11), (1.84, 0.04, 0.02), mat_disp_glow)

    # Baked Goods on Display:
    # Tier 1 (Bottom shelf Z=0.70): Colorful cookies and croissants
    for xi, cx in enumerate([-2.1, -1.8, -1.5, -1.2, -0.9, -0.65]):
        # Baking paper / tray
        create_box(f"Int_Display_Paper_B_{xi}", (cx, -1.45, 0.70), (0.24, 0.38, 0.005), mat_flour_sack)
        # Low poly cookies
        for row in [-0.12, 0.0, 0.12]:
            c_obj = create_cylinder(f"Int_Cookie_B_{xi}_{row}", (cx, -1.45 + row, 0.715), 0.045, 0.015, mat_cookie_gold, segments=8)
            # Chocolate chips on top
            create_box(f"Int_Chip_B_{xi}_{row}", (cx, -1.45 + row, 0.725), (0.02, 0.02, 0.01), mat_cookie_choc)

    # Tier 2 (Middle shelf Z=0.92): Glazed donuts, croissants, and space for the baker's incoming tray!
    # Left side has croissants and donuts
    for xi, cx in enumerate([-2.1, -1.8]):
        # Croissants (stylized golden arc/cylinder)
        crois = create_cylinder(f"Int_Croissant_{xi}", (cx, -1.45, 0.93), 0.06, 0.16, mat_pastry_crois, segments=8)
        crois.rotation_euler.x = math.radians(90)
    for xi, cx in enumerate([-0.9, -0.65]):
        # Donuts with pink strawberry glaze
        d_base = create_cylinder(f"Int_Donut_{xi}", (cx, -1.45, 0.93), 0.055, 0.03, mat_cookie_gold, segments=10)
        d_glaze = create_cylinder(f"Int_Donut_Glaze_{xi}", (cx, -1.45, 0.945), 0.052, 0.01, mat_pastry_pink, segments=10)

    # Top of Display Case (Z = 1.14): Cupcake stands and glass display cloches
    for xi, cx in enumerate([-2.0, -1.4, -0.8]):
        # Cute wooden pedestal stand
        create_cylinder(f"Int_Stand_Base_{xi}", (cx, -1.45, 1.15), 0.12, 0.02, mat_white_trim, segments=12)
        create_cylinder(f"Int_Stand_Pillar_{xi}", (cx, -1.45, 1.19), 0.03, 0.06, mat_white_trim, segments=8)
        create_cylinder(f"Int_Stand_Plate_{xi}", (cx, -1.45, 1.23), 0.14, 0.02, mat_white_trim, segments=12)
        # Cupcake on top
        create_cylinder(f"Int_Cupcake_Base_{xi}", (cx, -1.45, 1.26), 0.045, 0.04, mat_flour_sack, segments=8)
        create_cylinder(f"Int_Cupcake_Icing_{xi}", (cx, -1.45, 1.29), 0.05, 0.03, mat_pastry_pink, segments=8)

    # -------------------------------------------------------------------------
    # Right Section: POS Cashier Station (X from -0.45 to +1.55)
    # -------------------------------------------------------------------------
    # Counter body
    create_box("Int_POS_Base", (0.55, -1.45, 0.60), (2.00, 0.65, 0.80), mat_counter_base)
    # Warm Honey Oak Countertop
    create_box("Int_POS_Top",  (0.55, -1.45, 1.02), (2.06, 0.70, 0.05), mat_counter_oak)

    # Decorative panel molding on customer side
    create_box("Int_POS_Front_Trim1", (0.05, -1.12, 0.60), (0.80, 0.02, 0.60), mat_white_trim)
    create_box("Int_POS_Front_Trim2", (1.05, -1.12, 0.60), (0.80, 0.02, 0.60), mat_white_trim)

    # POS Touchscreen Terminal (at X = 0.10, Y = -1.45, Z = 1.05)
    create_box("Int_POS_Stand", (0.10, -1.45, 1.12), (0.10, 0.10, 0.14), mat_oven_metal)
    pos_screen = create_box("Int_POS_Screen", (0.10, -1.42, 1.24), (0.28, 0.03, 0.20), mat_oven_metal)
    pos_screen.rotation_euler.x = math.radians(-30) # angled nicely for viewing
    pos_display = create_box("Int_POS_Display", (0.10, -1.40, 1.24), (0.24, 0.01, 0.16), mat_disp_glow)
    pos_display.rotation_euler.x = math.radians(-30)

    # Card Reader Terminal (at X = -0.15, Y = -1.30, Z = 1.05)
    create_box("Int_POS_CardReader", (-0.15, -1.30, 1.07), (0.10, 0.14, 0.04), mat_oven_metal)

    # Tip Jar (Glass jar with coins, at X = 0.40, Y = -1.30, Z = 1.05)
    create_cylinder("Int_TipJar_Glass", (0.40, -1.30, 1.13), 0.065, 0.15, mat_disp_glass, segments=10)
    create_cylinder("Int_TipJar_Lid",   (0.40, -1.30, 1.21), 0.068, 0.02, mat_brass, segments=10)
    for ci in range(4):
        create_cylinder(f"Int_TipCoin_{ci}", (0.39 + ci*0.01, -1.30, 1.08 + ci*0.015), 0.025, 0.008, mat_brass, segments=8)

    # Takeout Paper Bags (at X = 0.75, Y = -1.45, Z = 1.05)
    for bi, by in enumerate([-1.50, -1.40]):
        create_box(f"Int_PaperBag_{bi}", (0.75, by, 1.16), (0.16, 0.10, 0.22), mat_flour_sack)

    # Large Glass Cookie Jars (at X = 1.15, 1.40, Y = -1.40, Z = 1.05)
    for ji, jx in enumerate([1.12, 1.38]):
        create_cylinder(f"Int_CookieJar_Glass_{ji}", (jx, -1.40, 1.18), 0.09, 0.25, mat_disp_glass, segments=12)
        create_cylinder(f"Int_CookieJar_Lid_{ji}",   (jx, -1.40, 1.31), 0.095, 0.03, mat_brass, segments=12)
        create_cylinder(f"Int_CookieJar_Knob_{ji}",  (jx, -1.40, 1.34), 0.025, 0.03, mat_brass, segments=8)
        # Cookies inside
        for ki in range(3):
            create_cylinder(f"Int_JarCookie_{ji}_{ki}", (jx, -1.40, 1.10 + ki*0.05), 0.06, 0.03, mat_cookie_gold, segments=8)

    # -------------------------------------------------------------------------
    # 6. Baking Area (Background: Oven, Cooling Rack, Prep Table, Sacks)
    # -------------------------------------------------------------------------
    # Commercial Bakery Oven (at X = -1.95, Y = -2.95, Z from 0.20 to 1.85)
    create_box("Int_Oven_Body", (-1.95, -2.95, 0.95), (1.10, 0.55, 1.50), mat_oven_metal)
    # Stainless legs
    for lx in [-2.42, -1.48]:
        for ly in [-3.18, -2.72]:
            create_box(f"Int_Oven_Leg_{lx}_{ly}", (lx, ly, 0.28), (0.06, 0.06, 0.16), mat_brass)

    # Oven Doors with Glowing Chambers (Emission #FF6600)
    for di, dz in enumerate([0.65, 1.25]):
        # Frame
        create_box(f"Int_Oven_DoorFrame_{di}", (-1.95, -2.67, dz), (0.92, 0.04, 0.42), mat_oven_metal)
        # Glass window showing glowing fire/heat
        create_box(f"Int_Oven_Window_{di}",    (-1.95, -2.66, dz), (0.76, 0.02, 0.28), mat_oven_glow)
        # Heavy brass pull handle
        create_box(f"Int_Oven_Handle_{di}",    (-1.95, -2.63, dz), (0.50, 0.03, 0.04), mat_brass)

    # Control Panel & Temperature Gauges
    create_box("Int_Oven_ControlPanel", (-1.95, -2.67, 1.62), (0.95, 0.03, 0.14), mat_oven_metal)
    for gi in range(3):
        create_cylinder(f"Int_Oven_Dial_{gi}", (-2.20 + gi*0.25, -2.65, 1.62), 0.035, 0.02, mat_brass, segments=10)

    # Exhaust Hood & Duct above oven
    create_box("Int_Oven_Hood", (-1.95, -2.95, 2.05), (1.20, 0.65, 0.35), mat_oven_metal)
    create_cylinder("Int_Oven_Duct", (-1.95, -2.95, 2.65), 0.15, 0.85, mat_oven_metal, segments=12)

    # Multi-Tier Rolling Baker's Cooling Rack (at X = -0.65, Y = -2.90, Z = 0.20 to 1.80)
    # 4 Corner steel uprights
    for rx in [-0.95, -0.35]:
        for ry in [-3.12, -2.68]:
            create_box(f"Int_Rack_Pole_{rx}_{ry}", (rx, ry, 1.00), (0.04, 0.04, 1.60), mat_oven_metal)
            # Caster wheels at bottom
            create_cylinder(f"Int_Rack_Wheel_{rx}_{ry}", (rx, ry, 0.24), 0.03, 0.04, mat_oven_metal, segments=8)

    # 4 Wire Shelves holding cookie trays
    for si, sz in enumerate([0.55, 0.85, 1.15, 1.45]):
        # Shelf frame
        create_box(f"Int_Rack_Shelf_{si}", (-0.65, -2.90, sz), (0.60, 0.44, 0.02), mat_oven_metal)
        # Aluminum baking sheet tray
        create_box(f"Int_Rack_Tray_{si}",  (-0.65, -2.90, sz + 0.02), (0.56, 0.40, 0.015), mat_white_trim)
        # Freshly baked chocolate chip cookies on tray
        for ci, cx in enumerate([-0.82, -0.65, -0.48]):
            for ri, ry in enumerate([-3.02, -2.90, -2.78]):
                create_cylinder(f"Int_Rack_Cookie_{si}_{ci}_{ri}", (cx, ry, sz + 0.035), 0.04, 0.015, mat_cookie_gold, segments=8)
                create_box(f"Int_Rack_Chip_{si}_{ci}_{ri}", (cx, ry, sz + 0.045), (0.015, 0.015, 0.01), mat_cookie_choc)

    # Baker's Prep Table & Wooden Rolling Pins (at X = 0.85, Y = -2.95, Z = 0.95)
    create_box("Int_PrepTable_Top",  (0.85, -2.95, 0.88), (1.40, 0.55, 0.06), mat_counter_oak)
    for tx in [0.22, 1.48]:
        for ty in [-3.18, -2.72]:
            create_box(f"Int_PrepTable_Leg_{tx}_{ty}", (tx, ty, 0.54), (0.06, 0.06, 0.65), mat_white_trim)

    # Wooden cutting board and mixing bowl on prep table
    create_box("Int_Prep_Board", (0.50, -2.95, 0.92), (0.35, 0.25, 0.02), mat_wood_floor)
    create_cylinder("Int_Prep_Bowl", (0.90, -2.95, 0.98), 0.12, 0.14, mat_white_trim, segments=12)
    # Wooden rolling pin
    pin = create_cylinder("Int_RollingPin", (1.30, -2.95, 0.93), 0.025, 0.32, mat_counter_oak, segments=10)
    pin.rotation_euler.y = math.radians(90)

    # Flour Sacks on Floor (at X = 1.85, 2.15, Y = -2.85, Z = 0.20)
    for fi, (fx, fy, frot) in enumerate([(1.85, -2.85, 15), (2.15, -2.80, -20)]):
        sack = create_box(f"Int_FlourSack_{fi}", (fx, fy, 0.42), (0.32, 0.26, 0.40), mat_flour_sack)
        sack.rotation_euler.z = math.radians(frot)
        # Tied neck at top
        tie = create_box(f"Int_FlourSack_Tie_{fi}", (fx, fy, 0.64), (0.16, 0.14, 0.06), mat_wood_floor)
        tie.rotation_euler.z = math.radians(frot)

    # Back Wall Chalkboard MENU (at X = 0.10, Y = -3.22, Z = 2.15)
    create_box("Int_Menu_Frame", (0.10, -3.22, 2.15), (1.60, 0.04, 0.95), mat_counter_oak)
    create_box("Int_Menu_Board", (0.10, -3.21, 2.15), (1.48, 0.02, 0.83), mat_chalkboard)
    # Chalkboard stylized text bars
    create_box("Int_Menu_Title", (0.10, -3.20, 2.45), (0.90, 0.01, 0.06), mat_chalk_txt)
    for li, lz in enumerate([2.30, 2.18, 2.06, 1.94, 1.82]):
        create_box(f"Int_Menu_Line_{li}", (0.10, -3.20, lz), (1.10 - (li % 2)*0.25, 0.01, 0.03), mat_chalk_txt)

    # Floating Back Shelves with Jars (at X = 1.95, Y = -3.22, Z = 1.80 and 2.30)
    for shi, shz in enumerate([1.80, 2.25]):
        create_box(f"Int_WallShelf_{shi}", (1.95, -3.20, shz), (1.10, 0.22, 0.04), mat_counter_oak)
        for ji in range(4):
            jx = 1.55 + ji * 0.26
            j_col = [mat_cookie_gold, mat_pastry_pink, mat_flour_sack, mat_cookie_choc][ji % 4]
            create_cylinder(f"Int_ShelfJar_{shi}_{ji}", (jx, -3.20, shz + 0.10), 0.055, 0.15, j_col, segments=8)
            create_cylinder(f"Int_ShelfLid_{shi}_{ji}", (jx, -3.20, shz + 0.185), 0.06, 0.02, mat_brass, segments=8)

    # -------------------------------------------------------------------------
    # 7. Ceiling Pendant Lights with Warm Glow & Point Lights
    # -------------------------------------------------------------------------
    light_positions = [
        ("DispLight",  -1.40, -1.45, 2.45),
        ("POSLight",    0.55, -1.45, 2.45),
        ("BakingLight",-0.65, -2.60, 2.45),
    ]

    for lname, lx, ly, lz in light_positions:
        # Thin cord from ceiling (Z = 3.05 down to 2.45)
        create_cylinder(f"Int_Cord_{lname}", (lx, ly, (3.05 + lz)/2), 0.008, 3.05 - lz, mat_oven_metal, segments=6)
        # Pastel shade
        shade = create_cylinder(f"Int_Shade_{lname}", (lx, ly, lz + 0.08), 0.18, 0.12, mat_mint_panel, segments=12)
        # Glowing bulb
        create_cylinder(f"Int_Bulb_{lname}", (lx, ly, lz + 0.02), 0.06, 0.08, mat_pendant_glow, segments=8)

        # Blender Point Light
        light_data_name = f"Data_Light_{lname}"
        light_obj_name = f"Light_{lname}"

        light_data = bpy.data.lights.get(light_data_name)
        if not light_data:
            light_data = bpy.data.lights.new(name=light_data_name, type='POINT')
        light_data.energy = 45.0  # Warm, bright 45W
        light_data.color = (1.0, 0.72, 0.42) # Warm golden #FFAE52
        light_data.shadow_soft_size = 0.35

        light_obj = bpy.data.objects.get(light_obj_name)
        if not light_obj:
            light_obj = bpy.data.objects.new(name=light_obj_name, object_data=light_data)
            link_obj(light_obj)
        light_obj.location = (lx, ly, lz - 0.05)

    # -------------------------------------------------------------------------
    # 8. Animated Baker Character ("Pelayan")
    # -------------------------------------------------------------------------
    # Model cute, stylized low-poly character
    # Clean hierarchy:
    # Character_Root (Empty)
    #   ├── Baker_Hips
    #   │     ├── Baker_Torso (Shirt + Apron)
    #   │     │     ├── Baker_Head (Face + Hat)
    #   │     │     ├── Baker_Arm_L -> Forearm_L -> Hand_L
    #   │     │     └── Baker_Arm_R -> Forearm_R -> Hand_R
    #   │     ├── Baker_Leg_L -> Foot_L
    #   │     └── Baker_Leg_R -> Foot_R

    # Clean up any previous baker objects
    baker_names = [o.name for o in bpy.data.objects if o.name.startswith("Baker_") or o.name.startswith("BakerProp_")]
    for bn in baker_names:
        bo = bpy.data.objects.get(bn)
        if bo:
            bpy.data.objects.remove(bo, do_unlink=True)

    # Root Empty for translation and global rotation
    root_empty = bpy.data.objects.new("Baker_Root", None)
    root_empty.empty_display_type = 'ARROWS'
    root_empty.empty_display_size = 0.5
    link_obj(root_empty)
    root_empty.location = (-0.65, -2.55, 0.20)
    root_empty.rotation_euler = (0, 0, math.radians(180)) # facing -Y towards cooling rack initially

    def add_baker_part(name, loc, size, mat, parent=None, is_cyl=False, radius=0.1, depth=0.2, segments=10):
        if is_cyl:
            mesh = bpy.data.meshes.new(name + "_Mesh")
            obj = bpy.data.objects.new(name, mesh)
            link_obj(obj)
            bm = bmesh.new()
            bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                                  radius1=radius, radius2=radius, depth=depth)
            bm.to_mesh(mesh)
            bm.free()
        else:
            mesh = bpy.data.meshes.new(name + "_Mesh")
            obj = bpy.data.objects.new(name, mesh)
            link_obj(obj)
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts:
                v.co.x *= size[0]
                v.co.y *= size[1]
                v.co.z *= size[2]
            bm.to_mesh(mesh)
            bm.free()

        obj.location = loc
        if mat:
            obj.data.materials.append(mat)
        if parent:
            obj.parent = parent
        return obj

    # Hips / Pelvis (Local Z = 0.70)
    hips = add_baker_part("Baker_Hips", (0, 0, 0.70), (0.28, 0.18, 0.16), mat_baker_pants, parent=root_empty)

    # Torso (Local Z = 0.22 above hips)
    torso = add_baker_part("Baker_Torso", (0, 0, 0.22), (0.32, 0.22, 0.32), mat_baker_shirt, parent=hips)

    # Apron Body & Bow (Local on Torso)
    add_baker_part("Baker_Apron_Front", (0, -0.115, -0.02), (0.28, 0.02, 0.32), mat_baker_apron, parent=torso)
    add_baker_part("Baker_Apron_Skirt", (0, -0.115, -0.22), (0.30, 0.02, 0.22), mat_baker_apron, parent=hips)
    add_baker_part("Baker_Apron_Bow",   (0, 0.115, -0.08),  (0.12, 0.04, 0.08), mat_baker_apron, parent=torso)

    # Head (Local Z = 0.28 above Torso)
    head = add_baker_part("Baker_Head", (0, 0, 0.28), (0.26, 0.24, 0.26), mat_baker_skin, parent=torso)

    # Cute Facial Features (Cute low-poly eyes, nose, blush)
    add_baker_part("Baker_Eye_L", (-0.06, -0.125, 0.01), (0.025, 0.01, 0.025), mat_oven_metal, parent=head)
    add_baker_part("Baker_Eye_R", (0.06, -0.125, 0.01),  (0.025, 0.01, 0.025), mat_oven_metal, parent=head)
    add_baker_part("Baker_Blush_L", (-0.08, -0.123, -0.04), (0.035, 0.01, 0.02), mat_baker_apron, parent=head)
    add_baker_part("Baker_Blush_R", (0.08, -0.123, -0.04),  (0.035, 0.01, 0.02), mat_baker_apron, parent=head)
    add_baker_part("Baker_Smile", (0.0, -0.123, -0.06), (0.05, 0.01, 0.015), mat_baker_shoes, parent=head)

    # Chef's Toque (Classic puffy white pleated hat)
    add_baker_part("Baker_Hat_Band", (0, 0, 0.15), None, mat_baker_hat, parent=head, is_cyl=True, radius=0.13, depth=0.06, segments=12)
    add_baker_part("Baker_Hat_Puff", (0, 0, 0.27), None, mat_baker_hat, parent=head, is_cyl=True, radius=0.20, depth=0.20, segments=12)

    # Arms and Hands
    # Left Arm
    arm_l = add_baker_part("Baker_Arm_L", (-0.20, 0, 0.10), (0.10, 0.10, 0.20), mat_baker_shirt, parent=torso)
    forearm_l = add_baker_part("Baker_Forearm_L", (0, 0, -0.16), (0.08, 0.08, 0.18), mat_baker_skin, parent=arm_l)
    hand_l = add_baker_part("Baker_Hand_L", (0, 0, -0.12), (0.07, 0.09, 0.08), mat_baker_skin, parent=forearm_l)

    # Right Arm
    arm_r = add_baker_part("Baker_Arm_R", (0.20, 0, 0.10), (0.10, 0.10, 0.20), mat_baker_shirt, parent=torso)
    forearm_r = add_baker_part("Baker_Forearm_R", (0, 0, -0.16), (0.08, 0.08, 0.18), mat_baker_skin, parent=arm_r)
    hand_r = add_baker_part("Baker_Hand_R", (0, 0, -0.12), (0.07, 0.09, 0.08), mat_baker_skin, parent=forearm_r)

    # Legs and Shoes
    # Left Leg
    leg_l = add_baker_part("Baker_Leg_L", (-0.08, 0, -0.20), (0.11, 0.12, 0.28), mat_baker_pants, parent=hips)
    add_baker_part("Baker_Shoe_L", (0, -0.03, -0.18), (0.12, 0.18, 0.10), mat_baker_shoes, parent=leg_l)

    # Right Leg
    leg_r = add_baker_part("Baker_Leg_R", (0.08, 0, -0.20), (0.11, 0.12, 0.28), mat_baker_pants, parent=hips)
    add_baker_part("Baker_Shoe_R", (0, -0.03, -0.18), (0.12, 0.18, 0.10), mat_baker_shoes, parent=leg_r)

    # The Baker's Baking Tray Prop (Carried during animation!)
    tray_prop = create_box("BakerProp_Tray", (0, 0, 0), (0.42, 0.32, 0.015), mat_white_trim)
    # 8 Low Poly Cookies on the tray
    for row in [-0.09, 0.09]:
        for col in [-0.14, -0.05, 0.05, 0.14]:
            c = create_cylinder(f"BakerProp_Cookie_{row}_{col}", (col, row, 0.015), 0.035, 0.012, mat_cookie_gold, segments=8)
            c.parent = tray_prop
            ch = create_box(f"BakerProp_Chip_{row}_{col}", (col, row, 0.024), (0.012, 0.012, 0.008), mat_cookie_choc)
            ch.parent = tray_prop

    # -------------------------------------------------------------------------
    # 9. Keyframing Complete 240-Frame Animation Cycle (24 fps, 10s loop)
    # -------------------------------------------------------------------------
    # Frame 1–30: Stands at rack, bends forward, reaches to pick up tray.
    # Frame 31–70: Turns around to face front (+Y), walks 3 steps to front counter holding tray level.
    # Frame 71–110: Bends down at display case, reaches arms inside, slides tray onto middle shelf.
    # Frame 111–130: Releases tray, pulls hands back, stands upright.
    # Frame 131–180: Steps to POS cashier, wipes apron, turns head toward door, raises right arm and waves cheerfully!
    # Frame 181–220: Lowers arm, turns back around, walks back to cooling rack.
    # Frame 221–240: Sinks back into resting pose at rack, matching Frame 1 perfectly!

    anim_objects = [root_empty, torso, head, arm_l, forearm_l, arm_r, forearm_r, leg_l, leg_r, tray_prop]
    for o in anim_objects:
        o.animation_data_clear()

    def set_kf(obj, prop, val, f):
        setattr(obj, prop, val)
        obj.keyframe_insert(data_path=prop, frame=f)

    # Keyframe Root (Location & Z-Rotation)
    # Positions:
    # At Rack: (-0.65, -2.55, 0.20)
    # Walking: (-0.65 -> -1.25, -2.55 -> -1.85)
    # At Display: (-1.25, -1.85, 0.20)
    # At POS: (-0.40, -1.85, 0.20)
    # Return: (-0.40 -> -0.65, -1.85 -> -2.55)

    root_keyframes = [
        (1,   (-0.65, -2.55, 0.20), math.radians(180)),
        (25,  (-0.65, -2.55, 0.20), math.radians(180)),
        (35,  (-0.65, -2.55, 0.20), math.radians(120)),
        (50,  (-0.95, -2.20, 0.20), math.radians(40)),
        (65,  (-1.25, -1.85, 0.20), math.radians(0)),
        (110, (-1.25, -1.85, 0.20), math.radians(0)),
        (120, (-1.10, -1.85, 0.20), math.radians(10)),
        (135, (-0.40, -1.85, 0.20), math.radians(15)),
        (175, (-0.40, -1.85, 0.20), math.radians(15)),
        (185, (-0.40, -1.85, 0.20), math.radians(90)),
        (205, (-0.55, -2.25, 0.20), math.radians(150)),
        (220, (-0.65, -2.55, 0.20), math.radians(180)),
        (240, (-0.65, -2.55, 0.20), math.radians(180)),
    ]

    for f, loc, rot_z in root_keyframes:
        set_kf(root_empty, "location", Vector(loc), f)
        set_kf(root_empty, "rotation_euler", Euler((0, 0, rot_z)), f)

    # Keyframe Torso bend / breathing
    torso_keyframes = [
        (1,   (0, 0, 0.22), Euler((math.radians(10), 0, 0))),
        (20,  (0, 0, 0.18), Euler((math.radians(35), 0, 0))), # bending down to rack
        (30,  (0, 0, 0.22), Euler((math.radians(5), 0, 0))),  # lifting tray
        (50,  (0, 0, 0.23), Euler((math.radians(0), 0, 0))),  # carrying
        (70,  (0, 0, 0.22), Euler((math.radians(5), 0, 0))),
        (85,  (0, 0, 0.16), Euler((math.radians(32), 0, 0))), # bending to slide tray in shelf
        (105, (0, 0, 0.16), Euler((math.radians(32), 0, 0))),
        (120, (0, 0, 0.22), Euler((math.radians(0), 0, 0))),  # standing upright
        (140, (0, 0, 0.22), Euler((math.radians(-3), 0, 0))), # proud customer posture
        (170, (0, 0, 0.22), Euler((math.radians(-3), 0, 0))),
        (185, (0, 0, 0.22), Euler((math.radians(0), 0, 0))),
        (205, (0, 0, 0.23), Euler((math.radians(4), 0, 0))),
        (225, (0, 0, 0.22), Euler((math.radians(10), 0, 0))),
        (240, (0, 0, 0.22), Euler((math.radians(10), 0, 0))),
    ]
    for f, loc, rot in torso_keyframes:
        set_kf(torso, "location", Vector(loc), f)
        set_kf(torso, "rotation_euler", rot, f)

    # Keyframe Head (Nodding and looking around)
    head_keyframes = [
        (1,   Euler((math.radians(15), 0, 0))),
        (20,  Euler((math.radians(25), 0, 0))),
        (35,  Euler((math.radians(0), 0, 0))),
        (65,  Euler((math.radians(15), 0, 0))),
        (85,  Euler((math.radians(28), 0, 0))),
        (115, Euler((math.radians(0), 0, 0))),
        (135, Euler((math.radians(-5), 0, math.radians(-15)))), # looking toward door
        (145, Euler((math.radians(10), 0, math.radians(-15)))), # friendly nod
        (155, Euler((math.radians(-5), 0, math.radians(-15)))),
        (165, Euler((math.radians(10), 0, math.radians(-15)))), # second nod
        (175, Euler((math.radians(0), 0, 0))),
        (220, Euler((math.radians(15), 0, 0))),
        (240, Euler((math.radians(15), 0, 0))),
    ]
    for f, rot in head_keyframes:
        set_kf(head, "rotation_euler", rot, f)

    # Arms Animation: Holding tray, extending, waving
    # Left Arm
    arm_l_keyframes = [
        (1,   Euler((math.radians(20), 0, 0)), Euler((math.radians(-30), 0, 0))),
        (20,  Euler((math.radians(65), 0, 0)), Euler((math.radians(-70), 0, 0))), # grabbing tray
        (35,  Euler((math.radians(45), 0, 0)), Euler((math.radians(-80), 0, 0))), # holding level
        (65,  Euler((math.radians(45), 0, 0)), Euler((math.radians(-80), 0, 0))),
        (85,  Euler((math.radians(70), 0, 0)), Euler((math.radians(-50), 0, 0))), # extending into shelf
        (105, Euler((math.radians(70), 0, 0)), Euler((math.radians(-50), 0, 0))),
        (120, Euler((math.radians(15), 0, 0)), Euler((math.radians(-20), 0, 0))), # relaxing
        (140, Euler((math.radians(10), 0, 0)), Euler((math.radians(-25), 0, 0))), # wiping apron
        (170, Euler((math.radians(10), 0, 0)), Euler((math.radians(-25), 0, 0))),
        (185, Euler((math.radians(25), 0, 0)), Euler((math.radians(-30), 0, 0))),
        (220, Euler((math.radians(20), 0, 0)), Euler((math.radians(-30), 0, 0))),
        (240, Euler((math.radians(20), 0, 0)), Euler((math.radians(-30), 0, 0))),
    ]
    for f, r_arm, r_fore in arm_l_keyframes:
        set_kf(arm_l, "rotation_euler", r_arm, f)
        set_kf(forearm_l, "rotation_euler", r_fore, f)

    # Right Arm: Holding tray, then cheerfully WAVING to customer at frames 140–165!
    arm_r_keyframes = [
        (1,   Euler((math.radians(20), 0, 0)), Euler((math.radians(-30), 0, 0))),
        (20,  Euler((math.radians(65), 0, 0)), Euler((math.radians(-70), 0, 0))), # grabbing tray
        (35,  Euler((math.radians(45), 0, 0)), Euler((math.radians(-80), 0, 0))), # holding level
        (65,  Euler((math.radians(45), 0, 0)), Euler((math.radians(-80), 0, 0))),
        (85,  Euler((math.radians(70), 0, 0)), Euler((math.radians(-50), 0, 0))), # extending into shelf
        (105, Euler((math.radians(70), 0, 0)), Euler((math.radians(-50), 0, 0))),
        (120, Euler((math.radians(15), 0, 0)), Euler((math.radians(-20), 0, 0))),
        # CHEERFUL WAVE TO CUSTOMER!
        (135, Euler((math.radians(130), math.radians(-30), 0)), Euler((math.radians(-40), 0, math.radians(-20)))),
        (145, Euler((math.radians(140), math.radians(-40), 0)), Euler((math.radians(-40), 0, math.radians(-40)))), # wave right
        (152, Euler((math.radians(135), math.radians(-25), 0)), Euler((math.radians(-40), 0, math.radians(10)))),  # wave left
        (159, Euler((math.radians(140), math.radians(-40), 0)), Euler((math.radians(-40), 0, math.radians(-40)))), # wave right
        (166, Euler((math.radians(135), math.radians(-25), 0)), Euler((math.radians(-40), 0, math.radians(10)))),  # wave left
        (175, Euler((math.radians(10), 0, 0)), Euler((math.radians(-15), 0, 0))), # lower arm
        (185, Euler((math.radians(25), 0, 0)), Euler((math.radians(-30), 0, 0))),
        (220, Euler((math.radians(20), 0, 0)), Euler((math.radians(-30), 0, 0))),
        (240, Euler((math.radians(20), 0, 0)), Euler((math.radians(-30), 0, 0))),
    ]
    for f, r_arm, r_fore in arm_r_keyframes:
        set_kf(arm_r, "rotation_euler", r_arm, f)
        set_kf(forearm_r, "rotation_euler", r_fore, f)

    # Legs walking cycle during walks:
    # Walk 1: f=35 to 65 (3 steps)
    # Walk 2: f=185 to 215 (3 steps)
    leg_keyframes = [
        (1,   0, 0),
        (35,  0, 0),
        (42,  math.radians(28),  math.radians(-28)),
        (49,  math.radians(-28), math.radians(28)),
        (56,  math.radians(28),  math.radians(-28)),
        (65,  0, 0),
        (130, 0, 0),
        (185, 0, 0),
        (192, math.radians(28),  math.radians(-28)),
        (199, math.radians(-28), math.radians(28)),
        (206, math.radians(28),  math.radians(-28)),
        (215, 0, 0),
        (240, 0, 0),
    ]
    for f, rot_l, rot_r in leg_keyframes:
        set_kf(leg_l, "rotation_euler", Euler((rot_l, 0, 0)), f)
        set_kf(leg_r, "rotation_euler", Euler((rot_r, 0, 0)), f)

    # Baking Tray Prop Animation (follows hands seamlessly then rests on display shelf!)
    # Positions in world coordinates:
    # At Rack: (-0.65, -2.90, 1.15)
    # Held by baker:
    #   f=30: (-0.65, -2.75, 1.15)
    #   f=50: (-0.95, -2.00, 1.15)
    #   f=65: (-1.25, -1.65, 1.15)
    # Reaching into shelf:
    #   f=85: (-1.25, -1.45, 0.92)  (placed on display shelf)
    #   f=110..240: stays resting on shelf at (-1.25, -1.45, 0.92)
    tray_keyframes = [
        (1,   (-0.65, -2.90, 1.15), 0),
        (20,  (-0.65, -2.90, 1.15), 0),
        (30,  (-0.65, -2.75, 1.15), 0),
        (38,  (-0.70, -2.45, 1.15), math.radians(-40)),
        (50,  (-0.95, -2.00, 1.15), math.radians(-110)),
        (65,  (-1.25, -1.65, 1.15), math.radians(-180)),
        (85,  (-1.25, -1.45, 0.92), math.radians(-180)), # on middle shelf
        (110, (-1.25, -1.45, 0.92), math.radians(-180)),
        (240, (-1.25, -1.45, 0.92), math.radians(-180)),
    ]
    for f, loc, rot_z in tray_keyframes:
        set_kf(tray_prop, "location", Vector(loc), f)
        set_kf(tray_prop, "rotation_euler", Euler((0, 0, rot_z)), f)

    # -------------------------------------------------------------------------
    # 10. Camera Setup: "Camera_Interior"
    # -------------------------------------------------------------------------
    # Positioned inside the shop at eye-level (~1.5m), wide-angle (22mm),
    # capturing the counter, illuminated display case, baker, oven, and exterior view through window/door!
    cam_name = "Camera_Interior"
    cam_data = bpy.data.cameras.get(cam_name)
    if not cam_data:
        cam_data = bpy.data.cameras.new(cam_name)
    cam_data.lens = 22.0 # 22mm wide-angle lens
    cam_data.sensor_width = 36.0
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0

    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        cam_col = bpy.data.collections.get("Camera")
        if cam_col:
            cam_col.objects.link(cam_obj)
        else:
            scene.collection.objects.link(cam_obj)

    # Position in front right corner looking across at baker, display case, oven, and front entrance
    cam_obj.location = (1.95, -0.65, 1.48)
    # Calculate aim toward center of baker & display case (-0.8, -1.8, 1.10)
    target = Vector((-0.80, -1.80, 1.10))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

    print("Animated Interior build completed successfully!")

if __name__ == "__main__":
    run_build()
