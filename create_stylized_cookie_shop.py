import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Euler, Matrix
import random

def build_scene():
    def hex_to_linear(hex_str, alpha=1.0):
        hex_str = hex_str.lstrip('#')
        r, g, b = [int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
        def srgb_to_lin(c):
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        return (srgb_to_lin(r), srgb_to_lin(g), srgb_to_lin(b), alpha)

    # -------------------------------------------------------------------------
    # 1. Clean Scene
    # -------------------------------------------------------------------------
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    for collection in list(bpy.data.collections):
        bpy.data.collections.remove(collection)
    for block in list(bpy.data.meshes):
        if block.users == 0: bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        if block.users == 0: bpy.data.materials.remove(block)
    for block in list(bpy.data.lights):
        if block.users == 0: bpy.data.lights.remove(block)
    for block in list(bpy.data.cameras):
        if block.users == 0: bpy.data.cameras.remove(block)

    # -------------------------------------------------------------------------
    # 2. Collections Setup (Building, Props, Lighting, Camera, Vegetation)
    # -------------------------------------------------------------------------
    scene = bpy.context.scene
    colls = {}
    for name in ["Building", "Props", "Vegetation", "Lighting", "Camera"]:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
        colls[name] = c

    def link_to(obj, c_name):
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        colls[c_name].objects.link(obj)
        return obj

    # -------------------------------------------------------------------------
    # 3. Materials Setup
    # -------------------------------------------------------------------------
    def make_mat(name, color_rgba, roughness=0.7, metallic=0.0, emission=None, emission_strength=1.0, transmission=0.0, alpha=1.0):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        
        bsdf.inputs['Base Color'].default_value = color_rgba
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = transmission
            
        if 'Alpha' in bsdf.inputs:
            bsdf.inputs['Alpha'].default_value = alpha
            
        if emission:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = emission
                bsdf.inputs['Emission Strength'].default_value = emission_strength
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = emission
                if 'Emission Strength' in bsdf.inputs:
                    bsdf.inputs['Emission Strength'].default_value = emission_strength
                    
        mat.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
        
        if alpha < 1.0 or transmission > 0:
            if hasattr(mat, 'blend_method'):
                mat.blend_method = 'BLEND'
            if hasattr(mat, 'shadow_method'):
                mat.shadow_method = 'NONE'
        return mat

    # Exact Hex Colors specified
    c_mint = hex_to_linear("#A2D5C6")          # Pastel Mint
    c_peach = hex_to_linear("#F8C5A8")         # Peach
    c_pink = hex_to_linear("#F4B2B2")          # Soft Pink
    c_cream = hex_to_linear("#F9F3EB")         # Warm Cream
    c_cookie = hex_to_linear("#D49B6A")        # Cookie Brown
    c_choc = hex_to_linear("#4A2C18")          # Dark Chocolate
    c_dark_iron = hex_to_linear("#2E3033")     # Dark Iron/Metal
    c_brass = hex_to_linear("#D4AF37")         # Brass Gold
    c_sidewalk = hex_to_linear("#B5B0AB")      # Gray Stone Sidewalk
    c_curb = hex_to_linear("#8A8580")          # Curb Stone
    c_road = hex_to_linear("#34363A")          # Dark Asphalt
    c_tree_wood = hex_to_linear("#6E4F32")     # Tree Trunk Wood
    c_foliage_1 = hex_to_linear("#68B058")     # Foliage Green 1
    c_foliage_2 = hex_to_linear("#82C76A")     # Foliage Green 2
    c_flower_pink = hex_to_linear("#FF7B90")   # Flower Pink
    c_flower_yellow = hex_to_linear("#FFDA44") # Flower Yellow
    c_chalkboard = hex_to_linear("#232526")    # Chalkboard Dark Gray
    c_warm_glow = (1.0, 0.84, 0.52, 1.0)       # Interior Warm Glow

    mat_mint = make_mat("Mat_Mint", c_mint, roughness=0.65)
    mat_peach = make_mat("Mat_Peach", c_peach, roughness=0.65)
    mat_pink = make_mat("Mat_SoftPink", c_pink, roughness=0.65)
    mat_cream = make_mat("Mat_WarmCream", c_cream, roughness=0.60)
    mat_cookie = make_mat("Mat_CookieBrown", c_cookie, roughness=0.85)
    mat_choc = make_mat("Mat_DarkChocolate", c_choc, roughness=0.35, metallic=0.0)
    mat_dark_iron = make_mat("Mat_DarkIron", c_dark_iron, roughness=0.50, metallic=0.7)
    mat_brass = make_mat("Mat_Brass", c_brass, roughness=0.30, metallic=0.85)
    mat_sidewalk = make_mat("Mat_Sidewalk", c_sidewalk, roughness=0.88)
    mat_curb = make_mat("Mat_Curb", c_curb, roughness=0.80)
    mat_road = make_mat("Mat_Road", c_road, roughness=0.92)
    mat_tree_wood = make_mat("Mat_TreeWood", c_tree_wood, roughness=0.80)
    mat_foliage_1 = make_mat("Mat_Foliage1", c_foliage_1, roughness=0.75)
    mat_foliage_2 = make_mat("Mat_Foliage2", c_foliage_2, roughness=0.75)
    mat_flower_pink = make_mat("Mat_FlowerPink", c_flower_pink, roughness=0.50)
    mat_flower_yellow = make_mat("Mat_FlowerYellow", c_flower_yellow, roughness=0.50)
    mat_chalkboard = make_mat("Mat_Chalkboard", c_chalkboard, roughness=0.80)
    mat_glass = make_mat("Mat_Glass", (0.88, 0.95, 1.0, 0.25), roughness=0.08, transmission=0.85, alpha=0.25)
    mat_glow = make_mat("Mat_InteriorGlow", c_warm_glow, roughness=0.3, emission=c_warm_glow, emission_strength=4.0)
    mat_gold_text = make_mat("Mat_GoldSignText", (1.0, 0.88, 0.42, 1.0), roughness=0.25, metallic=0.75, emission=(1.0, 0.88, 0.42, 1.0), emission_strength=1.2)
    mat_pastry_bread = make_mat("Mat_BreadLoaf", hex_to_linear("#C98642"), roughness=0.8)
    mat_white_road_line = make_mat("Mat_RoadLine", hex_to_linear("#EAE4D8"), roughness=0.8)

    # -------------------------------------------------------------------------
    # Helper Modeling Functions
    # -------------------------------------------------------------------------
    def box(name, coll_name, loc, size, mat=None):
        bpy.ops.mesh.primitive_cube_add(location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = (size[0]/2, size[1]/2, size[2]/2)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if mat:
            obj.data.materials.append(mat)
        return link_to(obj, coll_name)

    def cyl(name, coll_name, loc, r, h, segs=16, mat=None, rot=(0,0,0)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=segs, radius=r, depth=h, location=loc, rotation=rot)
        obj = bpy.context.active_object
        obj.name = name
        if mat:
            obj.data.materials.append(mat)
        return link_to(obj, coll_name)

    def sphere(name, coll_name, loc, r, segs=12, rings=8, mat=None):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=rings, radius=r, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        if mat:
            obj.data.materials.append(mat)
        return link_to(obj, coll_name)

    def icosphere(name, coll_name, loc, r, subdiv=1, mat=None):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv, radius=r, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        if mat:
            obj.data.materials.append(mat)
        return link_to(obj, coll_name)

    # =========================================================================
    # 4. BUILDING ARCHITECTURE (Two-Story Shop)
    # =========================================================================
    # Foundation Plinth (Warm Cream Stone)
    box("Plinth_Base", "Building", (0, -1.7, 0.18), (6.3, 3.6, 0.36), mat_cream)

    # First Floor Main Body (Pastel Mint Green #A2D5C6)
    box("Floor1_Walls", "Building", (0, -1.7, 1.70), (6.0, 3.4, 2.70), mat_mint)

    # First Floor Peach Paneling Inserts (under the left and right display windows)
    box("F1_Panel_Left", "Building", (-1.85, 0.02, 0.50), (2.05, 0.08, 0.36), mat_peach)
    box("F1_Panel_Right", "Building", (1.85, 0.02, 0.50), (2.05, 0.08, 0.36), mat_peach)
    box("F1_Panel_Trim_L", "Building", (-1.85, 0.04, 0.50), (2.12, 0.04, 0.42), mat_cream)
    box("F1_Panel_Trim_R", "Building", (1.85, 0.04, 0.50), (2.12, 0.04, 0.42), mat_cream)

    # White Trim Molding between Floor 1 and Floor 2 (Mid-cornice band)
    box("Mid_Cornice_Lower", "Building", (0, 0.05, 3.12), (6.35, 0.45, 0.12), mat_cream)
    box("Mid_Cornice_Upper", "Building", (0, 0.08, 3.24), (6.45, 0.50, 0.14), mat_cream)

    # Second Floor Main Body (Pastel Peach #F8C5A8)
    box("Floor2_Walls", "Building", (0, -1.7, 4.45), (6.0, 3.4, 2.30), mat_peach)

    # White Corner Pilasters / Trim Columns
    for px in [-3.05, 3.05]:
        box(f"Pilaster_{px}", "Building", (px, 0.02, 2.9), (0.35, 0.45, 5.7), mat_cream)
        box(f"Pilaster_Cap_{px}", "Building", (px, 0.04, 5.75), (0.45, 0.55, 0.20), mat_cream)

    # Roof Cornice & Detailing (Z: 5.6 to 6.6m)
    box("Roof_Cornice_Main", "Building", (0, 0.08, 5.65), (6.5, 0.55, 0.18), mat_cream)
    for di in range(-7, 8):
        dx = di * 0.40
        box(f"Roof_Dentil_{di}", "Building", (dx, 0.30, 5.56), (0.16, 0.14, 0.10), mat_cream)
    
    # Parapet Wall
    box("Roof_Parapet", "Building", (0, -1.7, 6.00), (6.1, 3.5, 0.55), mat_peach)
    box("Roof_Parapet_Trim", "Building", (0, 0.06, 6.28), (6.3, 0.45, 0.12), mat_cream)

    # Center Decorative Pediment Arch on Parapet
    cyl("Roof_Arch_Pediment", "Building", (0, 0.04, 6.28), r=1.05, h=0.25, segs=28, mat=mat_peach, rot=(math.radians(90), 0, 0))
    cyl("Roof_Arch_Rim", "Building", (0, 0.08, 6.28), r=1.12, h=0.20, segs=28, mat=mat_cream, rot=(math.radians(90), 0, 0))
    sphere("Roof_Finial_Orb", "Building", (0, 0.08, 7.50), r=0.22, segs=16, rings=12, mat=mat_gold_text)

    # Chimney on Left Roof
    box("Roof_Chimney", "Building", (-2.2, -1.2, 6.55), (0.65, 0.65, 1.20), mat_cream)
    box("Roof_Chimney_Cap", "Building", (-2.2, -1.2, 7.20), (0.80, 0.80, 0.14), mat_pink)
    cyl("Roof_Chimney_Pot", "Building", (-2.2, -1.2, 7.42), r=0.18, h=0.35, segs=12, mat=mat_cookie)

    # -------------------------------------------------------------------------
    # Entrance (Doorway, Door, Open Sign, Handle)
    # -------------------------------------------------------------------------
    box("Door_Architrave_L", "Building", (-0.68, 0.05, 1.35), (0.12, 0.16, 2.25), mat_cream)
    box("Door_Architrave_R", "Building", (0.68, 0.05, 1.35), (0.12, 0.16, 2.25), mat_cream)
    box("Door_Architrave_Top", "Building", (0, 0.05, 2.48), (1.48, 0.16, 0.12), mat_cream)
    box("Door_Pediment", "Building", (0, 0.08, 2.60), (1.60, 0.22, 0.12), mat_pink)
    box("Door_Step", "Building", (0, 0.22, 0.25), (1.60, 0.38, 0.12), mat_cream)

    box("Door_Slab", "Building", (0, 0.04, 1.30), (1.20, 0.08, 2.15), mat_peach)
    box("Door_Lower_Panel", "Building", (0, 0.09, 0.65), (0.90, 0.04, 0.68), mat_pink)
    box("Door_Glass_Pane", "Building", (0, 0.08, 1.70), (0.88, 0.03, 0.90), mat_glass)
    box("Door_Mullion_H", "Building", (0, 0.10, 1.70), (0.88, 0.03, 0.04), mat_cream)
    box("Door_Mullion_V", "Building", (0, 0.10, 1.70), (0.04, 0.03, 0.90), mat_cream)

    cyl("Door_Brass_Handle", "Building", (0.45, 0.13, 1.25), r=0.035, h=0.20, segs=8, mat=mat_brass, rot=(math.radians(90), 0, 0))
    box("Door_Brass_Kickplate", "Building", (0, 0.09, 0.26), (1.05, 0.02, 0.10), mat_brass)

    # "Open" Sign
    box("Door_Open_Sign_Board", "Building", (0, 0.105, 1.62), (0.36, 0.02, 0.16), mat_cream)
    box("Door_Open_Sign_Inner", "Building", (0, 0.118, 1.62), (0.32, 0.01, 0.12), mat_pink)
    bpy.ops.object.text_add(location=(0, 0.13, 1.57), rotation=(math.radians(90), 0, math.radians(180)))
    txt_open = bpy.context.active_object
    txt_open.name = "Text_Open"
    txt_open.data.body = "OPEN"
    txt_open.data.align_x = 'CENTER'
    txt_open.data.align_y = 'CENTER'
    txt_open.data.size = 0.08
    txt_open.data.extrude = 0.015
    txt_open.data.materials.append(mat_gold_text)
    link_to(txt_open, "Building")

    # -------------------------------------------------------------------------
    # Large Display Bay Windows (Left & Right)
    # -------------------------------------------------------------------------
    for side, xc in [("Left", -1.85), ("Right", 1.85)]:
        box(f"Bay_Sill_{side}", "Building", (xc, 0.18, 0.72), (2.05, 0.40, 0.14), mat_cream)
        box(f"Bay_Frame_Bottom_{side}", "Building", (xc, 0.12, 0.82), (1.95, 0.28, 0.08), mat_cream)
        box(f"Bay_Frame_Top_{side}", "Building", (xc, 0.12, 2.45), (1.95, 0.28, 0.08), mat_cream)
        box(f"Bay_Frame_L_{side}", "Building", (xc - 0.94, 0.12, 1.64), (0.08, 0.28, 1.60), mat_cream)
        box(f"Bay_Frame_R_{side}", "Building", (xc + 0.94, 0.12, 1.64), (0.08, 0.28, 1.60), mat_cream)
        
        box(f"Bay_Mullion_V_{side}", "Building", (xc, 0.22, 1.64), (0.05, 0.08, 1.56), mat_cream)
        box(f"Bay_Mullion_H1_{side}", "Building", (xc, 0.22, 1.25), (1.85, 0.08, 0.05), mat_cream)
        box(f"Bay_Mullion_H2_{side}", "Building", (xc, 0.22, 1.95), (1.85, 0.08, 0.05), mat_cream)

        box(f"Bay_Glass_Front_{side}", "Building", (xc, 0.20, 1.64), (1.85, 0.02, 1.56), mat_glass)
        box(f"Bay_Glass_SideL_{side}", "Building", (xc - 0.94, 0.10, 1.64), (0.02, 0.20, 1.56), mat_glass)
        box(f"Bay_Glass_SideR_{side}", "Building", (xc + 0.94, 0.10, 1.64), (0.02, 0.20, 1.56), mat_glass)

        box(f"Interior_GlowPlane_{side}", "Building", (xc, -0.65, 1.60), (1.80, 0.02, 1.40), mat_glow)

        box(f"Counter_{side}", "Building", (xc, -0.25, 0.65), (1.75, 0.60, 0.65), mat_cream)
        box(f"Counter_Top_{side}", "Building", (xc, -0.22, 1.00), (1.80, 0.65, 0.06), mat_cookie)

        for tier_i, tx in enumerate([-0.45, 0.45]):
            cyl(f"Stand_Base_{side}_{tier_i}", "Building", (xc + tx, -0.15, 1.05), r=0.16, h=0.04, segs=12, mat=mat_cream)
            cyl(f"Stand_Stem_{side}_{tier_i}", "Building", (xc + tx, -0.15, 1.15), r=0.035, h=0.18, segs=8, mat=mat_cream)
            cyl(f"Stand_Plate_{side}_{tier_i}", "Building", (xc + tx, -0.15, 1.25), r=0.28, h=0.025, segs=16, mat=mat_cream)

            if tier_i == 0:
                for a_deg in [0, 72, 144, 216, 288]:
                    rad = math.radians(a_deg)
                    k_x = xc + tx + 0.14 * math.cos(rad)
                    k_y = -0.15 + 0.14 * math.sin(rad)
                    cyl(f"Cookie_{side}_{a_deg}", "Building", (k_x, k_y, 1.28), r=0.05, h=0.02, segs=8, mat=mat_cookie)
                    cyl(f"Chip_{side}_{a_deg}", "Building", (k_x, k_y, 1.295), r=0.016, h=0.012, segs=5, mat=mat_choc)
            else:
                box(f"Bread1_{side}", "Building", (xc + tx - 0.08, -0.15, 1.28), (0.16, 0.08, 0.06), mat_pastry_bread)
                box(f"Bread2_{side}", "Building", (xc + tx + 0.08, -0.15, 1.28), (0.16, 0.08, 0.06), mat_pastry_bread)
                cyl(f"Pastry_{side}", "Building", (xc + tx, -0.15, 1.32), r=0.06, h=0.03, segs=10, mat=mat_pink)

    # -------------------------------------------------------------------------
    # Second Floor Windows & Sills (3 Multi-Pane Windows)
    # -------------------------------------------------------------------------
    for wi, wx in enumerate([-1.85, 0.0, 1.85]):
        box(f"F2_Sill_{wi}", "Building", (wx, 0.08, 3.82), (1.30, 0.22, 0.10), mat_cream)
        box(f"F2_Frame_B_{wi}", "Building", (wx, 0.04, 3.90), (1.20, 0.12, 0.06), mat_cream)
        box(f"F2_Frame_T_{wi}", "Building", (wx, 0.04, 5.15), (1.20, 0.12, 0.06), mat_cream)
        box(f"F2_Frame_L_{wi}", "Building", (wx - 0.58, 0.04, 4.52), (0.06, 0.12, 1.25), mat_cream)
        box(f"F2_Frame_R_{wi}", "Building", (wx + 0.58, 0.04, 4.52), (0.06, 0.12, 1.25), mat_cream)
        
        box(f"F2_Mullion_V_{wi}", "Building", (wx, 0.05, 4.52), (0.04, 0.08, 1.20), mat_cream)
        box(f"F2_Mullion_H_{wi}", "Building", (wx, 0.05, 4.52), (1.15, 0.08, 0.04), mat_cream)
        
        box(f"F2_Glass_{wi}", "Building", (wx, 0.03, 4.52), (1.15, 0.02, 1.20), mat_glass)
        box(f"F2_Glow_{wi}", "Building", (wx, -0.30, 4.52), (1.10, 0.02, 1.10), mat_glow)

        box(f"F2_Shutter_L_{wi}", "Building", (wx - 0.76, 0.05, 4.52), (0.28, 0.05, 1.22), mat_mint)
        box(f"F2_Shutter_R_{wi}", "Building", (wx + 0.76, 0.05, 4.52), (0.28, 0.05, 1.22), mat_mint)
        box(f"F2_Shutter_TrimL_{wi}", "Building", (wx - 0.76, 0.07, 4.52), (0.26, 0.02, 1.18), mat_cream)
        box(f"F2_Shutter_TrimR_{wi}", "Building", (wx + 0.76, 0.07, 4.52), (0.26, 0.02, 1.18), mat_cream)

    # -------------------------------------------------------------------------
    # Striped Fabric Awning (Pastel Pink #F4B2B2 & Warm Cream #F9F3EB)
    # -------------------------------------------------------------------------
    awning_w = 5.4
    num_stripes = 14
    stripe_w = awning_w / num_stripes
    
    for si in range(num_stripes):
        sx = -awning_w/2 + (si + 0.5) * stripe_w
        s_mat = mat_pink if si % 2 == 0 else mat_cream
        
        canopy = box(f"Awning_Stripe_{si}", "Building", (sx, 0.68, 2.55), (stripe_w * 0.98, 1.34, 0.04), s_mat)
        canopy.rotation_euler = (math.radians(26), 0, 0)
        
        box(f"Valance_Slab_{si}", "Building", (sx, 1.28, 2.08), (stripe_w * 0.98, 0.03, 0.24), s_mat)
        cyl(f"Valance_Scallop_{si}", "Building", (sx, 1.28, 1.96), r=stripe_w * 0.48, h=0.035, segs=12, mat=s_mat, rot=(math.radians(90), 0, 0))

    box("Awning_Bar", "Building", (0, 1.28, 2.22), (awning_w + 0.12, 0.06, 0.06), mat_dark_iron)
    for strut_x in [-2.55, 2.55]:
        cyl(f"Awning_Strut_{strut_x}", "Building", (strut_x, 0.68, 2.05), r=0.03, h=1.45, segs=8, mat=mat_dark_iron, rot=(math.radians(52), 0, 0))

    # -------------------------------------------------------------------------
    # Giant Cookie Sign (Mounted directly above awning/entrance)
    # -------------------------------------------------------------------------
    cookie_z = 3.42
    cookie_r = 0.70
    cookie_thick = 0.25

    cyl("Giant_Cookie_Dough", "Building", (0, 0.35, cookie_z), r=cookie_r, h=cookie_thick, segs=20, mat=mat_cookie, rot=(math.radians(94), 0, 0))
    g_cookie = bpy.data.objects["Giant_Cookie_Dough"]
    bev_c = g_cookie.modifiers.new(name="Bevel", type='BEVEL')
    bev_c.width = 0.06
    bev_c.segments = 2

    chip_coords = [
        (0.00, 0.06, 0.13, 20),
        (-0.35, 0.25, 0.12, 45),
        (0.36, 0.22, 0.13, -30),
        (-0.25, -0.22, 0.14, 60),
        (0.32, -0.24, 0.12, 10),
        (0.04, 0.42, 0.11, -50),
        (-0.48, -0.02, 0.12, 35),
        (0.48, 0.02, 0.13, -65),
        (-0.16, 0.22, 0.10, 115),
        (0.18, -0.08, 0.11, 85),
        (-0.12, -0.42, 0.10, -20),
        (0.12, 0.48, 0.09, 40),
    ]
    for idx, (cx, cz, cr, crot) in enumerate(chip_coords):
        cy = 0.35 + cookie_thick/2 + 0.02
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=cr, radius2=cr*0.35, depth=cr*1.2, location=(cx, cy, cookie_z + cz), rotation=(math.radians(94), 0, math.radians(crot)))
        chip = bpy.context.active_object
        chip.name = f"Giant_Chip_{idx}"
        chip.data.materials.append(mat_choc)
        link_to(chip, "Building")

    for bx in [-0.5, 0.5]:
        box(f"Cookie_Bracket_{bx}", "Building", (bx, 0.18, cookie_z - 0.2), (0.05, 0.32, 0.50), mat_dark_iron)
        cyl(f"Cookie_Scroll_{bx}", "Building", (bx, 0.25, cookie_z - 0.45), r=0.12, h=0.04, segs=12, mat=mat_dark_iron, rot=(0, math.radians(90), 0))

    # Spotlights aimed at Giant Cookie
    for lamp_x in [-0.85, 0.85]:
        cyl(f"Cookie_SpotFixture_{lamp_x}", "Building", (lamp_x, 0.12, cookie_z + 0.65), r=0.06, h=0.04, segs=8, mat=mat_brass, rot=(math.radians(90), 0, 0))
        box(f"Cookie_SpotArm_{lamp_x}", "Building", (lamp_x, 0.32, cookie_z + 0.70), (0.03, 0.38, 0.03), mat_brass)
        
        bpy.ops.mesh.primitive_cone_add(radius1=0.12, radius2=0.04, depth=0.12, location=(lamp_x, 0.50, cookie_z + 0.62), rotation=(math.radians(35), 0, 0))
        c_shade = bpy.context.active_object
        c_shade.name = f"Cookie_SpotShade_{lamp_x}"
        c_shade.data.materials.append(mat_brass)
        link_to(c_shade, "Building")

        spot_data = bpy.data.lights.new(name=f"Spot_Cookie_{lamp_x}", type='SPOT')
        spot_data.energy = 40.0
        spot_data.color = (1.0, 0.90, 0.70)
        spot_data.spot_size = math.radians(55)
        spot_data.spot_blend = 0.35
        spot_obj = bpy.data.objects.new(name=f"Spot_Cookie_{lamp_x}", object_data=spot_data)
        spot_obj.location = (lamp_x, 0.52, cookie_z + 0.60)
        spot_obj.rotation_euler = (math.radians(-50), 0, 0)
        link_to(spot_obj, "Lighting")

    # -------------------------------------------------------------------------
    # Store Signage ("Cookie Shop" 3D Extruded Text)
    # -------------------------------------------------------------------------
    sign_z = 4.65
    box("Sign_Board_Backer", "Building", (0, 0.18, sign_z), (3.10, 0.08, 0.70), mat_choc)
    box("Sign_Board_Inner", "Building", (0, 0.22, sign_z), (2.95, 0.03, 0.56), mat_choc)
    box("Sign_Frame_Top", "Building", (0, 0.23, sign_z + 0.32), (3.15, 0.08, 0.06), mat_cream)
    box("Sign_Frame_Bottom", "Building", (0, 0.23, sign_z - 0.32), (3.15, 0.08, 0.06), mat_cream)
    box("Sign_Frame_L", "Building", (-1.55, 0.23, sign_z), (0.06, 0.08, 0.70), mat_cream)
    box("Sign_Frame_R", "Building", (1.55, 0.23, sign_z), (0.06, 0.08, 0.70), mat_cream)

    for ix in [-1.22, 1.22]:
        cyl(f"Sign_MiniCookie_{ix}", "Building", (ix, 0.24, sign_z), r=0.15, h=0.03, segs=12, mat=mat_cookie, rot=(math.radians(90), 0, 0))
        for chip_i, (cx_off, cz_off) in enumerate([(-0.04, 0.04), (0.05, 0.03), (0.0, -0.05)]):
            cyl(f"Sign_Chip_{ix}_{chip_i}", "Building", (ix + cx_off, 0.26, sign_z + cz_off), r=0.03, h=0.02, segs=6, mat=mat_choc, rot=(math.radians(90), 0, 0))

    bpy.ops.object.text_add(location=(0, 0.26, sign_z - 0.12), rotation=(math.radians(90), 0, math.radians(180)))
    txt_cookie = bpy.context.active_object
    txt_cookie.name = "Text_CookieShop"
    txt_cookie.data.body = "Cookie Shop"
    txt_cookie.data.align_x = 'CENTER'
    txt_cookie.data.align_y = 'CENTER'
    txt_cookie.data.size = 0.36
    txt_cookie.data.extrude = 0.045
    txt_cookie.data.bevel_depth = 0.015
    txt_cookie.data.bevel_resolution = 2
    txt_cookie.data.materials.append(mat_gold_text)
    link_to(txt_cookie, "Building")

    # =========================================================================
    # 5. SIDEWALK & STREET ELEMENTS
    # =========================================================================
    box("Street_Road", "Props", (0, 5.2, 0.01), (18.0, 3.8, 0.02), mat_road)
    for rx in [-6.0, -3.0, 0.0, 3.0, 6.0]:
        box(f"Street_Line_{rx}", "Props", (rx, 5.5, 0.025), (1.5, 0.15, 0.01), mat_white_road_line)

    box("Sidewalk_Base", "Props", (0, 1.65, 0.10), (16.0, 3.3, 0.20), mat_sidewalk)
    box("Sidewalk_Curb", "Props", (0, 3.35, 0.11), (16.0, 0.16, 0.22), mat_curb)
    
    for px in [-6.0, -4.5, -3.0, -1.5, 0.0, 1.5, 3.0, 4.5, 6.0]:
        box(f"Sidewalk_TileV_{px}", "Props", (px, 1.65, 0.205), (0.03, 3.2, 0.01), mat_curb)
    for py in [1.1, 2.2]:
        box(f"Sidewalk_TileH_{py}", "Props", (0, py, 0.205), (15.8, 0.03, 0.01), mat_curb)

    # -------------------------------------------------------------------------
    # Cute Low-Poly Streetlamp (On Sidewalk, Left of center: X: 3.1, Y: 2.3)
    # Note: From camera perspective at +X, positive X is to the VIEWER'S LEFT!
    # -------------------------------------------------------------------------
    sl_x, sl_y = 3.1, 2.3
    box("Lamp_Plinth", "Props", (sl_x, sl_y, 0.30), (0.40, 0.40, 0.22), mat_dark_iron)
    cyl("Lamp_Base_Ring", "Props", (sl_x, sl_y, 0.44), r=0.18, h=0.12, segs=10, mat=mat_dark_iron)
    cyl("Lamp_Post", "Props", (sl_x, sl_y, 1.8), r=0.07, h=2.6, segs=8, mat=mat_dark_iron)
    box("Lamp_Arm", "Props", (sl_x - 0.22, sl_y, 3.1), (0.45, 0.08, 0.08), mat_dark_iron)
    cyl("Lamp_Lantern_Cap", "Props", (sl_x - 0.42, sl_y, 3.25), r=0.22, h=0.10, segs=6, mat=mat_dark_iron)
    cyl("Lamp_Lantern_Glass", "Props", (sl_x - 0.42, sl_y, 3.00), r=0.16, h=0.36, segs=6, mat=mat_glow)
    cyl("Lamp_Lantern_Base", "Props", (sl_x - 0.42, sl_y, 2.80), r=0.14, h=0.06, segs=6, mat=mat_dark_iron)
    
    lamp_lt = bpy.data.lights.new(name="Light_Streetlamp", type='POINT')
    lamp_lt.energy = 55.0
    lamp_lt.color = (1.0, 0.82, 0.50)
    lamp_lt.shadow_soft_size = 0.25
    lamp_lt_obj = bpy.data.objects.new(name="Light_Streetlamp", object_data=lamp_lt)
    lamp_lt_obj.location = (sl_x - 0.42, sl_y, 2.98)
    link_to(lamp_lt_obj, "Lighting")

    # -------------------------------------------------------------------------
    # Small Low-Poly Bicycle (Parked on viewer's LEFT: X: 3.9, Y: 1.8)
    # -------------------------------------------------------------------------
    bx, by, bz = 3.9, 1.8, 0.55
    for wi, wx in enumerate([-0.45, 0.45]):
        cyl(f"Bike_Wheel_{wi}", "Props", (bx + wx, by, 0.48), r=0.28, h=0.04, segs=14, mat=mat_dark_iron, rot=(math.radians(90), 0, 0))
        cyl(f"Bike_SpokeDisc_{wi}", "Props", (bx + wx, by, 0.48), r=0.25, h=0.015, segs=10, mat=mat_cream, rot=(math.radians(90), 0, 0))
        cyl(f"Bike_Hub_{wi}", "Props", (bx + wx, by, 0.48), r=0.05, h=0.06, segs=8, mat=mat_dark_iron, rot=(math.radians(90), 0, 0))

    cyl("Bike_Frame_Bottom", "Props", (bx, by, 0.48), r=0.02, h=0.90, segs=6, mat=mat_mint, rot=(0, math.radians(90), 0))
    cyl("Bike_Frame_SeatTube", "Props", (bx - 0.10, by, 0.65), r=0.02, h=0.45, segs=6, mat=mat_mint, rot=(0, math.radians(18), 0))
    cyl("Bike_Frame_DownTube", "Props", (bx + 0.12, by, 0.60), r=0.02, h=0.58, segs=6, mat=mat_mint, rot=(0, math.radians(-38), 0))
    cyl("Bike_Frame_TopTube", "Props", (bx + 0.08, by, 0.78), r=0.02, h=0.55, segs=6, mat=mat_mint, rot=(0, math.radians(82), 0))
    box("Bike_Saddle", "Props", (bx - 0.16, by, 0.90), (0.16, 0.10, 0.04), mat_choc)
    cyl("Bike_Stem", "Props", (bx + 0.35, by, 0.82), r=0.02, h=0.22, segs=6, mat=mat_dark_iron)
    box("Bike_Handlebars", "Props", (bx + 0.35, by, 0.92), (0.04, 0.42, 0.03), mat_dark_iron)
    box("Bike_Basket", "Props", (bx + 0.46, by, 0.85), (0.16, 0.26, 0.14), mat_cream)

    # -------------------------------------------------------------------------
    # Wooden/Metal Bench on Viewer's RIGHT Side + Flower Planter Box (X: -3.2, Y: 1.6)
    # -------------------------------------------------------------------------
    bench_x, bench_y = -3.2, 1.6
    for leg_x in [-0.55, 0.55]:
        cyl(f"Bench_Leg_F_{leg_x}", "Props", (bench_x + leg_x, bench_y - 0.20, 0.42), r=0.03, h=0.44, segs=8, mat=mat_dark_iron)
        cyl(f"Bench_Leg_B_{leg_x}", "Props", (bench_x + leg_x, bench_y + 0.20, 0.62), r=0.03, h=0.84, segs=8, mat=mat_dark_iron)
        box(f"Bench_Arm_{leg_x}", "Props", (bench_x + leg_x, bench_y, 0.65), (0.04, 0.44, 0.04), mat_dark_iron)
    
    for sy_off in [-0.15, -0.05, 0.05, 0.15]:
        box(f"Bench_SeatSlat_{sy_off}", "Props", (bench_x, bench_y + sy_off, 0.46), (1.25, 0.08, 0.025), mat_cookie)
    for sz_off in [0.70, 0.82, 0.94]:
        box(f"Bench_BackSlat_{sz_off}", "Props", (bench_x, bench_y + 0.20, sz_off), (1.25, 0.025, 0.08), mat_cookie)

    # Flower Planter Box beside Bench (X: -4.25, Y: 1.6)
    box("Bench_Planter_Box", "Props", (-4.25, 1.6, 0.40), (0.50, 0.50, 0.38), mat_cream)
    box("Bench_Planter_Trim", "Props", (-4.25, 1.6, 0.58), (0.54, 0.54, 0.04), mat_pink)
    icosphere("Bench_Planter_Bush", "Props", (-4.25, 1.6, 0.70), r=0.26, subdiv=1, mat=mat_foliage_1)
    for f_i, (fx, fy, f_mat) in enumerate([(-0.10, -0.08, mat_flower_pink), (0.10, 0.08, mat_flower_yellow), (0.0, 0.12, mat_flower_pink)]):
        sphere(f"Bench_Flower_{f_i}", "Props", (-4.25 + fx, 1.6 + fy, 0.86), r=0.06, segs=8, rings=6, mat=f_mat)

    # -------------------------------------------------------------------------
    # Potted Plants & A-Frame Menu Sign near Doorway
    # -------------------------------------------------------------------------
    for pi, px in enumerate([-1.05, 1.05]):
        cyl(f"Entrance_Pot_{pi}", "Props", (px, 0.48, 0.34), r=0.20, h=0.26, segs=10, mat=mat_choc)
        cyl(f"Entrance_Pot_Rim_{pi}", "Props", (px, 0.48, 0.48), r=0.22, h=0.05, segs=10, mat=mat_cookie)
        icosphere(f"Entrance_Bush_{pi}", "Props", (px, 0.48, 0.75), r=0.28, subdiv=1, mat=mat_foliage_1)
        sphere(f"Entrance_Flower_{pi}", "Props", (px, 0.48, 0.98), r=0.07, segs=8, rings=6, mat=mat_flower_pink)

    # Chalkboard A-Frame Menu Sign (near doorway, X: -1.35, Y: 1.35)
    af_x, af_y = -1.35, 1.35
    leg_f = box("Chalk_Leg_F", "Props", (af_x, af_y - 0.08, 0.58), (0.55, 0.04, 0.78), mat_choc)
    leg_f.rotation_euler = (math.radians(-12), 0, math.radians(-20))
    leg_b = box("Chalk_Leg_B", "Props", (af_x, af_y + 0.08, 0.58), (0.55, 0.04, 0.78), mat_choc)
    leg_b.rotation_euler = (math.radians(12), 0, math.radians(-20))
    
    chalk_face = box("Chalk_Face", "Props", (af_x, af_y - 0.10, 0.60), (0.45, 0.02, 0.60), mat_chalkboard)
    chalk_face.rotation_euler = (math.radians(-12), 0, math.radians(-20))
    cyl("Chalk_Doodle", "Props", (af_x + 0.02, af_y - 0.12, 0.72), r=0.08, h=0.02, segs=10, mat=mat_cream, rot=(math.radians(78), 0, math.radians(-20)))
    for li, lz in enumerate([0.55, 0.48, 0.42]):
        c_line = box(f"Chalk_Line_{li}", "Props", (af_x + 0.01, af_y - 0.12, lz), (0.30 - li*0.06, 0.015, 0.02), mat_cream)
        c_line.rotation_euler = (math.radians(-12), 0, math.radians(-20))

    # =========================================================================
    # 6. STYLIZED LOW-POLY TREES (Both Sides)
    # =========================================================================
    for ti, (tx, ty, t_scale) in enumerate([(-5.2, 1.6, 1.0), (5.2, 1.6, 0.95)]):
        cyl(f"Tree_Trunk_{ti}", "Vegetation", (tx, ty, 1.5 * t_scale), r=0.20 * t_scale, h=3.0 * t_scale, segs=7, mat=mat_tree_wood)
        
        icosphere(f"Tree_Canopy_Center_{ti}", "Vegetation", (tx, ty, 3.4 * t_scale), r=1.15 * t_scale, subdiv=1, mat=mat_foliage_1)
        cluster_offsets = [
            (0.55, 0.20, -0.30, mat_foliage_2, 0.75),
            (-0.50, -0.25, -0.25, mat_foliage_1, 0.80),
            (0.15, -0.45, 0.20, mat_foliage_2, 0.70),
            (-0.20, 0.45, 0.10, mat_foliage_1, 0.75),
            (0.00, 0.00, 0.65, mat_foliage_2, 0.85),
        ]
        for ci, (ox, oy, oz, c_mat, c_r) in enumerate(cluster_offsets):
            icosphere(f"Tree_Canopy_Cluster_{ti}_{ci}", "Vegetation", (tx + ox*t_scale, ty + oy*t_scale, (3.4 + oz)*t_scale), r=c_r*t_scale, subdiv=1, mat=c_mat)

    # =========================================================================
    # 7. LIGHTING & CAMERA SETUP
    # =========================================================================
    sun_data = bpy.data.lights.new(name="Sun_Key", type='SUN')
    sun_data.energy = 2.2
    sun_data.color = (1.0, 0.92, 0.82)
    sun_data.angle = math.radians(14)
    sun_obj = bpy.data.objects.new(name="Sun_Key", object_data=sun_data)
    sun_obj.location = (6.0, 9.0, 11.0)
    sun_obj.rotation_euler = (math.radians(-45), math.radians(22), math.radians(-32))
    link_to(sun_obj, "Lighting")

    sky_data = bpy.data.lights.new(name="Sky_Fill", type='SUN')
    sky_data.energy = 0.55
    sky_data.color = (0.75, 0.86, 1.0)
    sky_obj = bpy.data.objects.new(name="Sky_Fill", object_data=sky_data)
    sky_obj.location = (-6.0, 5.0, 9.0)
    sky_obj.rotation_euler = (math.radians(-50), math.radians(-25), math.radians(120))
    link_to(sky_obj, "Lighting")

    for side, xpos in [("L", -1.85), ("R", 1.85)]:
        in_lt = bpy.data.lights.new(name=f"Light_Interior_{side}", type='POINT')
        in_lt.energy = 140.0
        in_lt.color = (1.0, 0.80, 0.48)
        in_lt.shadow_soft_size = 0.35
        in_obj = bpy.data.objects.new(name=f"Light_Interior_{side}", object_data=in_lt)
        in_obj.location = (xpos, -0.30, 1.70)
        link_to(in_obj, "Lighting")

    door_lt = bpy.data.lights.new(name="Light_Door_Lantern", type='POINT')
    door_lt.energy = 60.0
    door_lt.color = (1.0, 0.85, 0.55)
    door_lt.shadow_soft_size = 0.25
    door_obj = bpy.data.objects.new(name="Light_Door_Lantern", object_data=door_lt)
    door_obj.location = (0.0, 0.25, 2.65)
    link_to(door_obj, "Lighting")

    target_empty = bpy.data.objects.new("Camera_Target", None)
    target_empty.location = (0.0, 0.8, 3.1)
    link_to(target_empty, "Camera")

    cam_data = bpy.data.cameras.new(name="Storefront_Camera")
    cam_data.lens = 32.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new(name="Storefront_Camera", object_data=cam_data)
    cam_obj.location = (2.2, 11.2, 5.2)
    
    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = target_empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'
    
    link_to(cam_obj, "Camera")
    scene.camera = cam_obj

    # -------------------------------------------------------------------------
    # 8. World & Render Settings (Eevee Optimization)
    # -------------------------------------------------------------------------
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("CookieShop_World")
        scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.76, 0.84, 0.92, 1.0)
        bg_node.inputs['Strength'].default_value = 0.65

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

    if hasattr(scene, 'eevee'):
        scene.eevee.taa_render_samples = 16

    if hasattr(scene, 'view_settings'):
        scene.view_settings.view_transform = 'AgX' if 'AgX' in [v.identifier for v in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Standard'
        scene.view_settings.look = 'Medium High Contrast' if 'Medium High Contrast' in [l.identifier for l in bpy.types.ColorManagedViewSettings.bl_rna.properties['look'].enum_items] else 'None'

    print("Refined Two-story Stylized Low-Poly Cookie Shop created successfully!")
    return "Complete scene generated successfully."

build_scene()
