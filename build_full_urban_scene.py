"""
build_full_urban_scene.py
Multi-Agent Blender Script:
Expands the Cookie Shop into a complete, lively low-poly nighttime urban streetscape.
Sub-Agents:
1. Architect & Urban Planner: Flanking buildings (Bookstore, Flower Shop, Apartments),
   background skyline towers, extended road, crosswalks, parked yellow taxi & compact car, street props.
2. Interior Specialist: Complete interior, illuminated display case, POS station, oven, rack, menu.
3. Character Designer & Animator: 240-frame animated baker, 2 seated cafe patrons, walking pedestrians & dog.
4. Lighting & Director: Deep indigo night sky, cool moonlight, warm shop/streetlamp glows,
   twinkling stars (oscillating sinusoids), Camera_City_Street & Camera_Interior.
Collections:
- Collection_City
- Collection_Interior
- Collection_Characters
- Collection_Lighting
- Collection_Sky
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Matrix

def run_expansion():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.frame_start = 1
    scene.frame_end = 240
    scene.render.fps = 24
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    # EEVEE Optimization Settings
    if hasattr(scene, "eevee"):
        scene.eevee.fast_gi_method = 'AMBIENT_OCCLUSION_ONLY'
        scene.eevee.use_fast_gi = True
        scene.eevee.fast_gi_quality = 0.5
        scene.eevee.fast_gi_ray_count = 2
        scene.eevee.fast_gi_step_count = 6
        scene.eevee.taa_render_samples = 16

    # -------------------------------------------------------------------------
    # Target Collections Setup
    # -------------------------------------------------------------------------
    col_names = [
        "Collection_City",
        "Collection_Interior",
        "Collection_Characters",
        "Collection_Lighting",
        "Collection_Sky"
    ]
    cols = {}
    for cname in col_names:
        c = bpy.data.collections.get(cname)
        if not c:
            c = bpy.data.collections.new(cname)
            scene.collection.children.link(c)
        cols[cname] = c

    def link_to_col(obj, target_cname):
        target_c = cols[target_cname]
        if obj.name not in target_c.objects:
            target_c.objects.link(obj)
        # Unlink from root scene collection if present
        if obj.name in scene.collection.objects:
            scene.collection.objects.unlink(obj)
        return obj

    # -------------------------------------------------------------------------
    # Reorganize Existing Objects into Target Collections
    # -------------------------------------------------------------------------
    # Move existing interior objects to Collection_Interior
    existing_int_col = bpy.data.collections.get("Cookie Shop")
    if existing_int_col:
        for o in list(existing_int_col.objects):
            link_to_col(o, "Collection_Interior")

    # Move existing characters to Collection_Characters
    baker_root = bpy.data.objects.get("Baker_Root")
    if baker_root:
        link_to_col(baker_root, "Collection_Characters")
        for child in baker_root.children_recursive:
            link_to_col(child, "Collection_Characters")

    # Move existing sky objects to Collection_Sky
    sky_col = bpy.data.collections.get("Night_Sky")
    if sky_col:
        for o in list(sky_col.objects):
            link_to_col(o, "Collection_Sky")

    # Move existing lighting objects to Collection_Lighting
    light_col = bpy.data.collections.get("Lighting")
    if light_col:
        for o in list(light_col.objects):
            link_to_col(o, "Collection_Lighting")

    # Move existing buildings and props to Collection_City
    for cname in ["Building", "Props", "Vegetation", "Backyard", "Front_Seating"]:
        c = bpy.data.collections.get(cname)
        if c:
            for o in list(c.objects):
                if o.type == 'LIGHT':
                    link_to_col(o, "Collection_Lighting")
                elif "cam" in o.name.lower():
                    pass
                else:
                    link_to_col(o, "Collection_City")

    # -------------------------------------------------------------------------
    # Material Helper
    # -------------------------------------------------------------------------
    def get_or_create_mat(name, base_color, roughness=0.6, metallic=0.0,
                           emission_color=None, emission_strength=0.0, alpha=1.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out_node = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

        if isinstance(base_color, str):
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

        if 'Alpha' in bsdf.inputs:
            bsdf.inputs['Alpha'].default_value = alpha

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

        if alpha < 1.0:
            mat.blend_method = 'BLEND'
            if hasattr(mat, 'shadow_method'):
                mat.shadow_method = 'NONE'

        return mat

    # Materials Palette
    mat_brick_red   = get_or_create_mat("Mat_City_BrickRed", "#8B4513", roughness=0.7)
    mat_brick_brown = get_or_create_mat("Mat_City_BrickBrown", "#A0522D", roughness=0.7)
    mat_slate_blue  = get_or_create_mat("Mat_City_SlateBlue", "#4A6572", roughness=0.6)
    mat_sage_green  = get_or_create_mat("Mat_City_SageGreen", "#588157", roughness=0.6)
    mat_cream_stone = get_or_create_mat("Mat_City_CreamStone", "#D8C3A5", roughness=0.55)
    mat_dark_iron   = get_or_create_mat("Mat_City_DarkIron", "#2B2D42", roughness=0.45, metallic=0.75)
    mat_asphalt_ext = get_or_create_mat("Mat_City_Asphalt", "#262A30", roughness=0.65)
    mat_white_paint = get_or_create_mat("Mat_City_WhitePaint", "#F5F5F5", roughness=0.4)
    mat_curb_gray   = get_or_create_mat("Mat_City_CurbGray", "#7F8C8D", roughness=0.6)
    mat_win_lit     = get_or_create_mat("Mat_City_WindowLit", "#FFEAA7", roughness=0.3, emission_color="#FFEAA7", emission_strength=3.5)
    mat_win_dark    = get_or_create_mat("Mat_City_WindowDark", "#1A2530", roughness=0.2)
    mat_skyline     = get_or_create_mat("Mat_City_SkylineTower", "#151B2E", roughness=0.8)
    mat_taxi_yellow = get_or_create_mat("Mat_City_TaxiYellow", "#F4D03F", roughness=0.4)
    mat_car_teal    = get_or_create_mat("Mat_City_CarTeal", "#2A9D8F", roughness=0.35)
    mat_car_tire    = get_or_create_mat("Mat_City_CarTire", "#1C1C1C", roughness=0.8)
    mat_car_headlight = get_or_create_mat("Mat_City_Headlight", "#FFF9E6", roughness=0.2, emission_color="#FFF9E6", emission_strength=5.0)
    mat_car_taillight = get_or_create_mat("Mat_City_Taillight", "#E63946", roughness=0.2, emission_color="#E63946", emission_strength=4.0)
    mat_wood_cedar  = get_or_create_mat("Mat_City_WoodCedar", "#8B5A2B", roughness=0.6)
    mat_hydrant_red = get_or_create_mat("Mat_City_HydrantRed", "#D62828", roughness=0.4)
    mat_human_skin  = get_or_create_mat("Mat_Char_Skin", "#FFD7C0", roughness=0.65)
    mat_human_coat1 = get_or_create_mat("Mat_Char_CoatTan", "#C99A65", roughness=0.7)
    mat_human_coat2 = get_or_create_mat("Mat_Char_CoatMaroon", "#800020", roughness=0.7)
    mat_human_jeans = get_or_create_mat("Mat_Char_Jeans", "#2C3E50", roughness=0.7)
    mat_dog_fur     = get_or_create_mat("Mat_Char_DogFur", "#D4A373", roughness=0.8)

    # Mesh Helper
    def create_box(name, loc, size, mat=None, target_col="Collection_City"):
        existing = bpy.data.objects.get(name)
        if existing:
            bpy.data.objects.remove(existing, do_unlink=True)
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        link_to_col(obj, target_col)
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

    def create_cyl(name, loc, radius, depth, mat=None, segments=12, target_col="Collection_City"):
        existing = bpy.data.objects.get(name)
        if existing:
            bpy.data.objects.remove(existing, do_unlink=True)
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        link_to_col(obj, target_col)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments,
                              radius1=radius, radius2=radius, depth=depth)
        bm.to_mesh(mesh)
        bm.free()
        obj.location = loc
        if mat:
            obj.data.materials.append(mat)
        return obj

    # =========================================================================
    # SUB-AGENT 1: ARCHITECT & URBAN PLANNER (Cityscape & Environment)
    # =========================================================================

    # 1. Extended Road & Sidewalk Across Entire Urban Block
    # Road: X in [-22, 22], Y in [3.2, 9.5], Z = 0.05
    create_box("City_Road_Extended", (0.0, 6.35, 0.05), (44.0, 6.30, 0.08), mat_asphalt_ext)
    # Sidewalks: X in [-22, 22], Y in [0.0, 3.2], Z = 0.15
    create_box("City_Sidewalk_LeftExt",  (-12.5, 1.60, 0.15), (19.0, 3.20, 0.12), mat_curb_gray)
    create_box("City_Sidewalk_RightExt", (12.5, 1.60, 0.15),  (19.0, 3.20, 0.12), mat_curb_gray)
    # Road white dashed centerline
    for d_i in range(-10, 11):
        create_box(f"City_Road_Line_{d_i}", (d_i * 2.0, 6.35, 0.095), (1.2, 0.16, 0.005), mat_white_paint)
    # White zebra crosswalk markings
    for zx in [-8.5, -8.0, -7.5, -7.0, -6.5, 6.5, 7.0, 7.5, 8.0, 8.5]:
        create_box(f"City_Zebra_{zx}", (zx, 6.35, 0.095), (0.35, 4.5, 0.005), mat_white_paint)

    # 2. Flanking Buildings Left:
    # Building L1 (Bookstore): X in [-8.8, -3.2], Y in [-3.5, 0.0], 3 stories, Brick Red
    create_box("City_Bld_L1_Main", (-6.0, -1.75, 4.40), (5.60, 3.50, 8.80), mat_brick_red)
    create_box("City_Bld_L1_RoofCornice", (-6.0, -1.75, 8.90), (5.80, 3.70, 0.25), mat_cream_stone)
    # Bookstore Ground Floor Display & Sign
    create_box("City_Bookstore_Frame", (-6.0, 0.04, 1.35), (4.80, 0.12, 2.30), mat_dark_iron)
    create_box("City_Bookstore_Window", (-6.0, 0.08, 1.35), (4.40, 0.04, 1.90), mat_win_lit)
    create_box("City_Bookstore_Sign", (-6.0, 0.14, 2.65), (3.50, 0.08, 0.45), mat_win_lit)
    create_box("City_Bookstore_Awning", (-6.0, 0.40, 2.25), (4.20, 0.70, 0.12), mat_sage_green)
    # Upper multi-pane windows on L1
    for fl_z in [4.5, 7.0]:
        for win_x in [-7.5, -6.0, -4.5]:
            create_box(f"City_L1_Win_{fl_z}_{win_x}", (win_x, 0.04, fl_z), (1.00, 0.08, 1.40), mat_win_lit)
            create_box(f"City_L1_Sill_{fl_z}_{win_x}", (win_x, 0.08, fl_z - 0.75), (1.15, 0.16, 0.10), mat_cream_stone)
    # Black iron fire escape on L1 facade
    for fe_z in [3.7, 6.2]:
        create_box(f"City_L1_FireEscape_{fe_z}", (-7.2, 0.45, fe_z), (1.80, 0.80, 0.06), mat_dark_iron)
        create_box(f"City_L1_FERailing_{fe_z}",   (-7.2, 0.85, fe_z + 0.35), (1.80, 0.04, 0.70), mat_dark_iron)
    # Rooftop water tower on L1
    create_box("City_L1_WT_Legs", (-7.0, -1.8, 9.4), (1.4, 1.4, 0.8), mat_dark_iron)
    create_cyl("City_L1_WaterTower", (-7.0, -1.8, 10.5), 0.9, 1.4, mat_wood_cedar, segments=12)

    # Building L2 (4-story Slate Blue Apartment): X in [-14.8, -9.0], Height = 12.0m
    create_box("City_Bld_L2_Main", (-11.9, -1.85, 6.00), (5.80, 3.70, 12.00), mat_slate_blue)
    create_box("City_Bld_L2_Cornice", (-11.9, -1.85, 12.10), (6.00, 3.90, 0.30), mat_cream_stone)
    for l2_z in [2.2, 5.0, 7.8, 10.5]:
        for l2_x in [-13.5, -11.9, -10.3]:
            w_mat = mat_win_lit if (int(l2_z + l2_x) % 2 == 0) else mat_win_dark
            create_box(f"City_L2_Win_{l2_z}_{l2_x}", (l2_x, 0.04, l2_z), (0.95, 0.08, 1.30), w_mat)

    # 3. Flanking Buildings Right:
    # Building R1 (Flower Shop): X in [3.2, 8.8], 3 stories, Pastel Cream Stone
    create_box("City_Bld_R1_Main", (6.0, -1.75, 4.50), (5.60, 3.50, 9.00), mat_cream_stone)
    create_box("City_Bld_R1_Cornice", (6.0, -1.75, 9.10), (5.80, 3.70, 0.25), mat_brick_brown)
    # Flower Shop Ground Floor Display & Sign
    create_box("City_Flower_Frame", (6.0, 0.04, 1.35), (4.80, 0.12, 2.30), mat_sage_green)
    create_box("City_Flower_Window", (6.0, 0.08, 1.35), (4.40, 0.04, 1.90), mat_win_lit)
    create_box("City_Flower_Sign", (6.0, 0.14, 2.65), (3.60, 0.08, 0.45), mat_win_lit)
    create_box("City_Flower_Awning", (6.0, 0.40, 2.25), (4.20, 0.70, 0.12), mat_brick_brown)
    # Flower planter boxes along the shop front
    create_box("City_Flower_Box1", (4.5, 0.25, 0.35), (1.20, 0.35, 0.30), mat_wood_cedar)
    create_box("City_Flower_Box2", (7.5, 0.25, 0.35), (1.20, 0.35, 0.30), mat_wood_cedar)
    for fl_z in [4.6, 7.2]:
        for win_x in [4.5, 6.0, 7.5]:
            create_box(f"City_R1_Win_{fl_z}_{win_x}", (win_x, 0.04, fl_z), (1.00, 0.08, 1.40), mat_win_lit)

    # Building R2 (5-story Brick Brown Apartment): X in [9.0, 15.0], Height = 14.5m
    create_box("City_Bld_R2_Main", (12.0, -1.85, 7.25), (6.00, 3.70, 14.50), mat_brick_brown)
    create_box("City_Bld_R2_Cornice", (12.0, -1.85, 14.60), (6.20, 3.90, 0.35), mat_cream_stone)
    for r2_z in [2.2, 5.0, 7.8, 10.6, 13.2]:
        for r2_x in [10.4, 12.0, 13.6]:
            w_mat = mat_win_lit if (int(r2_z + r2_x) % 2 == 1) else mat_win_dark
            create_box(f"City_R2_Win_{r2_z}_{r2_x}", (r2_x, 0.04, r2_z), (0.95, 0.08, 1.30), w_mat)
    # Fire escape on R2
    for fe_z in [4.2, 7.0, 9.8]:
        create_box(f"City_R2_FE_{fe_z}", (10.4, 0.45, fe_z), (1.80, 0.80, 0.06), mat_dark_iron)
        create_box(f"City_R2_FERail_{fe_z}", (10.4, 0.85, fe_z + 0.35), (1.80, 0.04, 0.70), mat_dark_iron)

    # 4. Background Skyline Silhouette Towers (City Depth, Y in [-16, -26])
    skyline_data = [
        (-18.0, -18.0, 7.0, 6.0, 22.0),
        (-12.0, -22.0, 6.5, 6.0, 26.0),
        (-5.0,  -20.0, 6.0, 5.5, 19.0),
        (2.0,   -24.0, 7.5, 6.0, 28.0),
        (8.0,   -19.0, 6.0, 5.5, 21.0),
        (15.0,  -22.0, 7.0, 6.0, 25.0),
        (21.0,  -18.0, 6.5, 6.0, 18.0),
    ]
    for s_i, (sx, sy, sw, sd, sh) in enumerate(skyline_data):
        create_box(f"City_Skyline_{s_i}", (sx, sy, sh/2), (sw, sd, sh), mat_skyline)
        # Glowing window grids on towers
        for wy in range(3, int(sh) - 2, 3):
            create_box(f"City_Skyline_Win_{s_i}_{wy}", (sx, sy + sd/2 + 0.05, wy), (sw * 0.75, 0.08, 0.8), mat_win_lit)

    # 5. Street Props: Fire Hydrant, Newspaper Box, Bike Rack, Trash Cans
    # Fire hydrant at X = -4.5, Y = 3.0
    create_cyl("City_Hydrant_Base", (-4.5, 3.0, 0.35), 0.14, 0.40, mat_hydrant_red, segments=10)
    create_cyl("City_Hydrant_Top",  (-4.5, 3.0, 0.60), 0.16, 0.16, mat_hydrant_red, segments=10)
    # Newspaper distribution boxes at X = -9.2, Y = 2.8
    create_box("City_NewsBox_Blue", (-9.2, 2.8, 0.65), (0.45, 0.40, 0.85), mat_slate_blue)
    create_box("City_NewsBox_Red",  (-8.6, 2.8, 0.65), (0.45, 0.40, 0.85), mat_hydrant_red)
    # Bicycle rack at X = 4.2, Y = 2.8
    for bri in range(3):
        create_box(f"City_BikeRack_Bar_{bri}", (4.2 + bri*0.4, 2.8, 0.55), (0.05, 0.50, 0.75), mat_dark_iron)
    # Street Trash Can at X = -3.2, Y = 2.8
    create_cyl("City_TrashCan", (-3.2, 2.8, 0.50), 0.25, 0.75, mat_dark_iron, segments=10)

    # 6. Parked Vehicles (Low-Poly Yellow Taxi & Compact Teal Car)
    # Yellow City Taxi: Parked at X = -4.2, Y = 4.8
    create_box("City_Taxi_Chassis", (-4.2, 4.8, 0.55), (3.60, 1.70, 0.55), mat_taxi_yellow)
    create_box("City_Taxi_Cabin",   (-4.2, 4.8, 1.00), (2.20, 1.50, 0.50), mat_taxi_yellow)
    create_box("City_Taxi_RoofSign",(-4.2, 4.8, 1.32), (0.60, 0.25, 0.15), mat_win_lit) # glowing taxi sign
    # Wheels
    for wx in [-5.3, -3.1]:
        for wy in [3.9, 5.7]:
            create_cyl(f"City_Taxi_Wheel_{wx}_{wy}", (wx, wy, 0.32), 0.32, 0.20, mat_car_tire, segments=10)
    # Headlights & Taillights
    create_box("City_Taxi_HeadL", (-2.38, 4.3, 0.55), (0.05, 0.25, 0.15), mat_car_headlight)
    create_box("City_Taxi_HeadR", (-2.38, 5.3, 0.55), (0.05, 0.25, 0.15), mat_car_headlight)
    create_box("City_Taxi_TailL", (-6.02, 4.3, 0.55), (0.05, 0.25, 0.15), mat_car_taillight)
    create_box("City_Taxi_TailR", (-6.02, 5.3, 0.55), (0.05, 0.25, 0.15), mat_car_taillight)

    # Compact Teal Car: Parked at X = 7.0, Y = 4.8
    create_box("City_Car_Chassis", (7.0, 4.8, 0.50), (3.20, 1.60, 0.50), mat_car_teal)
    create_box("City_Car_Cabin",   (6.9, 4.8, 0.92), (1.90, 1.45, 0.45), mat_slate_blue)
    for wx in [5.9, 8.1]:
        for wy in [3.95, 5.65]:
            create_cyl(f"City_Car_Wheel_{wx}_{wy}", (wx, wy, 0.30), 0.30, 0.18, mat_car_tire, segments=10)

    # =========================================================================
    # SUB-AGENT 3: CHARACTER DESIGNER & ANIMATOR (Pedestrians & Patrons)
    # =========================================================================

    def create_lowpoly_human(base_name, loc, coat_mat, pants_mat=mat_human_jeans, target_col="Collection_Characters"):
        # Root Empty
        h_root = bpy.data.objects.get(base_name + "_Root")
        if not h_root:
            h_root = bpy.data.objects.new(base_name + "_Root", None)
            link_to_col(h_root, target_col)
        h_root.location = loc

        # Hips
        hips = create_box(base_name + "_Hips", (0, 0, 0.75), (0.26, 0.18, 0.15), pants_mat, target_col)
        hips.parent = h_root
        # Torso
        torso = create_box(base_name + "_Torso", (0, 0, 0.22), (0.30, 0.22, 0.32), coat_mat, target_col)
        torso.parent = hips
        # Head
        head = create_box(base_name + "_Head", (0, 0, 0.26), (0.24, 0.22, 0.24), mat_human_skin, target_col)
        head.parent = torso
        # Legs
        leg_l = create_box(base_name + "_LegL", (-0.08, 0, -0.22), (0.10, 0.10, 0.30), pants_mat, target_col)
        leg_l.parent = hips
        leg_r = create_box(base_name + "_LegR", (0.08, 0, -0.22), (0.10, 0.10, 0.30), pants_mat, target_col)
        leg_r.parent = hips
        # Arms
        arm_l = create_box(base_name + "_ArmL", (-0.18, 0, 0.05), (0.08, 0.08, 0.30), coat_mat, target_col)
        arm_l.parent = torso
        arm_r = create_box(base_name + "_ArmR", (0.18, 0, 0.05), (0.08, 0.08, 0.30), coat_mat, target_col)
        arm_r.parent = torso

        return h_root, leg_l, leg_r, arm_l, arm_r

    # Pedestrian 1: Business commuter walking eastward (X: -11.0 -> 3.0)
    commuter_root, c_ll, c_lr, c_al, c_ar = create_lowpoly_human("Ped_Commuter", (-11.0, 2.0, 0.15), mat_slate_blue)
    commuter_root.rotation_euler.z = math.radians(90) # facing +X
    # Keyframe Commuter walk across 240 frames
    commuter_root.location = (-11.0, 2.0, 0.15)
    commuter_root.keyframe_insert("location", frame=1)
    commuter_root.location = (3.0, 2.0, 0.15)
    commuter_root.keyframe_insert("location", frame=240)

    # Pedestrians 2 & 3: Couple strolling westward (X: 10.0 -> -4.0)
    couple1_root, p1_ll, p1_lr, p1_al, p1_ar = create_lowpoly_human("Ped_Couple1", (10.0, 1.8, 0.15), mat_human_coat1)
    couple1_root.rotation_euler.z = math.radians(-90) # facing -X
    couple1_root.location = (10.0, 1.8, 0.15)
    couple1_root.keyframe_insert("location", frame=1)
    couple1_root.location = (-4.0, 1.8, 0.15)
    couple1_root.keyframe_insert("location", frame=240)

    couple2_root, p2_ll, p2_lr, p2_al, p2_ar = create_lowpoly_human("Ped_Couple2", (10.4, 2.2, 0.15), mat_human_coat2)
    couple2_root.rotation_euler.z = math.radians(-90)
    couple2_root.location = (10.4, 2.2, 0.15)
    couple2_root.keyframe_insert("location", frame=1)
    couple2_root.location = (-3.6, 2.2, 0.15)
    couple2_root.keyframe_insert("location", frame=240)

    # Pedestrian 4: Dog walker with cute low-poly puppy
    dogwalker_root, dw_ll, dw_lr, dw_al, dw_ar = create_lowpoly_human("Ped_DogWalker", (-3.0, 2.4, 0.15), mat_sage_green)
    dogwalker_root.rotation_euler.z = math.radians(90) # facing +X
    dogwalker_root.location = (-3.0, 2.4, 0.15)
    dogwalker_root.keyframe_insert("location", frame=1)
    dogwalker_root.location = (9.0, 2.4, 0.15)
    dogwalker_root.keyframe_insert("location", frame=240)

    # Low-poly cute puppy next to dogwalker
    dog_obj = create_box("Ped_Puppy", (-2.4, 2.7, 0.35), (0.45, 0.22, 0.32), mat_dog_fur, "Collection_Characters")
    dog_obj.parent = dogwalker_root

    # Animate walking leg swings on pedestrians (looping every 24 frames)
    for (leg_l, leg_r, arm_l, arm_r) in [(c_ll, c_lr, c_al, c_ar), (p1_ll, p1_lr, p1_al, p1_ar), (dw_ll, dw_lr, dw_al, dw_ar)]:
        for f in range(1, 241, 12):
            phase = (f // 12) % 2
            sw = math.radians(25) if phase == 0 else math.radians(-25)
            leg_l.rotation_euler.x = sw
            leg_r.rotation_euler.x = -sw
            arm_l.rotation_euler.x = -sw
            arm_r.rotation_euler.x = sw
            leg_l.keyframe_insert("rotation_euler", frame=f)
            leg_r.keyframe_insert("rotation_euler", frame=f)
            arm_l.keyframe_insert("rotation_euler", frame=f)
            arm_r.keyframe_insert("rotation_euler", frame=f)

    # 2 Seated Café Patrons at the front round table (at X = 2.1, Y = 1.35)
    patron1_root, _, _, _, _ = create_lowpoly_human("Patron_ChairL", (1.65, 1.35, 0.15), mat_human_coat1)
    patron1_root.rotation_euler.z = math.radians(90) # facing table (+X)
    patron2_root, _, _, _, _ = create_lowpoly_human("Patron_ChairR", (2.55, 1.35, 0.15), mat_human_coat2)
    patron2_root.rotation_euler.z = math.radians(-90) # facing table (-X)

    # =========================================================================
    # SUB-AGENT 4: LIGHTING, CINEMATOGRAPHY & OPTIMIZATION (Eevee Director)
    # =========================================================================

    # 1. World & Moon Light Setup
    world = scene.world
    if world and world.use_nodes:
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node:
            bg_node.inputs['Color'].default_value = (0.035, 0.051, 0.118, 1.0) # Deep midnight indigo #090D1E
            bg_node.inputs['Strength'].default_value = 0.25

    # Cool Moonlight
    moon_lt = bpy.data.lights.get("Light_Moon_Key")
    if not moon_lt:
        moon_lt = bpy.data.lights.new("Light_Moon_Key", 'SUN')
    moon_lt.energy = 0.65
    moon_lt.color = (0.61, 0.72, 1.0) # Soft cool pale-blue #9BB8FF

    moon_obj = bpy.data.objects.get("Sun_MoonLight")
    if not moon_obj:
        moon_obj = bpy.data.objects.new("Sun_MoonLight", moon_lt)
        link_to_col(moon_obj, "Collection_Lighting")
    moon_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-35))

    # 2. Twinkling Stars Animation across frames 1–240
    # Collect all star meshes in Collection_Sky and add smooth oscillating emission
    star_objs = [o for o in cols["Collection_Sky"].objects if "star" in o.name.lower()]
    for s_idx, s_obj in enumerate(star_objs):
        if s_obj.data and hasattr(s_obj.data, "materials") and len(s_obj.data.materials) > 0:
            m = s_obj.data.materials[0]
            if m and m.use_nodes:
                bsdf = m.node_tree.nodes.get("Principled BSDF")
                if bsdf and 'Emission Strength' in bsdf.inputs:
                    # Keyframe smooth oscillation
                    phase = (s_idx * 17) % 60
                    for kf in range(1, 241, 30):
                        st = 1.0 + 2.5 * math.sin(math.radians((kf + phase) * 3.0))
                        bsdf.inputs['Emission Strength'].default_value = max(0.4, st)
                        bsdf.inputs['Emission Strength'].keyframe_insert("default_value", frame=kf)

    # 3. Camera Setup: "Camera_City_Street"
    # Captures the full urban streetscape angled from above:
    cam_city = bpy.data.objects.get("Camera_City_Street")
    if not cam_city:
        cam_data = bpy.data.cameras.new("Camera_City_Street")
        cam_city = bpy.data.objects.new("Camera_City_Street", cam_data)
        link_to_col(cam_city, "Collection_City")
    cam_city.data.lens = 32.0 # Cinematic perspective
    cam_city.data.clip_start = 0.2
    cam_city.data.clip_end = 200.0
    cam_city.location = (2.8, 17.5, 9.8) # Elevated front perspective
    target_loc = Vector((0.0, 0.8, 2.5))
    dir_vec = target_loc - cam_city.location
    cam_city.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()

    # Save Blend file
    blend_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_urban_street.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Urban scene created and saved to: {blend_path}")

def render_urban_view():
    scene = bpy.context.scene
    cam_city = bpy.data.objects.get("Camera_City_Street")
    if cam_city:
        scene.camera = cam_city
        scene.frame_set(150)
        city_render_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_urban_render.png"
        scene.render.filepath = city_render_path
        print(f"Rendering full urban street view to {city_render_path}...")
        bpy.ops.render.render(write_still=True)
        print("Urban street render complete!")

if __name__ == "__main__":
    run_expansion()
    render_urban_view()
